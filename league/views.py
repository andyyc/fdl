from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from league.forms import JoinLeagueForm, LeagueForm, GeneralManagerForm
from league.models import League, LeagueTeam, GeneralManager, PredraftPick, RosterSettings, ScoringSettings, WeeklyRoster, RosterPlayer, LeagueWeek
from stats.models import Player, Game, PlayerGameStats, Week
from draft.models import Draft, DraftOrder, Pick
from bloop import settings
import random
import simplejson    

@login_required
def draft_league(request, lid):
    try:
        league = League.objects.get(lid=lid)
    except ObjectDoesNotExist:
        raise Http404
    
    if request.method == 'POST':
        lteams = league.leagueteam_set.all()
        draft = Draft.objects.create(league_week=league.current_week, 
                                     current_round=1, 
                                     current_pick_num=1)
        league.current_week.status = LeagueWeek.DRAFTING
        league.current_week.save()
        lteams = list(lteams)
        random.shuffle(lteams)
        for lteam in lteams:
            do = DraftOrder.objects.get_or_create(draft=draft,
                                                  league_team=lteam)
            roster = WeeklyRoster.objects.create(league_team=lteam)
            lteam.roster = roster
            lteam.save()
                
        rs = league.roster_settings
        max_positions = (rs.num_Q + rs.num_R + rs.num_W + rs.num_T + 
                         rs.num_W_T + rs.num_W_R + rs.num_W_R_T + 
                         rs.num_K + rs.num_D)
        num_teams = len(lteams)
        max_picks = max_positions * num_teams
        
        while draft.current_pick_num <= max_picks:            
            draft_round = draft.current_round
            pick_num = draft.current_pick_num
            lteam_drafter = lteams[(draft.current_pick_num-1)%num_teams]

            player, roster_position = get_next_pick(draft, lteam_drafter, rs)

            if player and roster_position:       
                Pick.objects.create(num=pick_num, 
                                    draft_round=draft_round,
                                    draft=draft,
                                    player=player,
                                    league_team=lteam_drafter)    
                RosterPlayer.objects.get_or_create(
                    weekly_roster=lteam_drafter.roster,
                    position=roster_position,
                    player=player)

            draft.current_pick_num += 1
            if(draft.current_pick_num != 1 and 
               (draft.current_pick_num-1)%num_teams==0):
                draft.current_round += 1
                
            draft.save()
            league.current_week.status = LeagueWeek.DRAFTED
            league.current_week.save()
            
    return HttpResponse("ok")

@login_required
def league_home(request, lid):
    try:
        league = League.objects.get(lid=lid)
    except ObjectDoesNotExist:
        raise Http404

    current_week = 1
    lteams = list(league.leagueteam_set.all())
    
    for lteam in lteams:
        if lteam.roster != None:
            lteam.fan_pts = lteam.roster.get_fan_pts()

    if False:
        lteams.sort(key=lambda lteam: lteam.fan_pts, reverse=True)

    return render_to_response("league/league_home.html",
                              {'lteams':lteams,
                               'league':league,
                               'LeagueWeek':LeagueWeek
                               },
                              context_instance=RequestContext(request))

def get_next_pick(draft, lteam_drafter, rs):
    all_picks = draft.picks
    player = None
    roster_position = None
    roster = lteam_drafter.roster
    roster_players = roster.rosterplayer_set
    predraft_picks = PredraftPick.objects.filter(gm=lteam_drafter.gm,
                                                 exclude=False)
    for possible_pick in predraft_picks:
        player = possible_pick.player
        roster_position = None

        if not all_picks.filter(id=player.id).exists():
            if player.position == 'QB':
                if roster_players.filter(position=RosterPlayer.Q).count() < rs.num_Q:
                    roster_position = RosterPlayer.Q
                    break
            elif player.position == 'RB':
                if roster_players.filter(position=RosterPlayer.R).count() < rs.num_R:
                    roster_position = RosterPlayer.R
                    break
                elif roster_players.filter(position='WR').count() < rs.num_W_R:
                    roster_position = 'WR'
                    break
                elif roster_players.filter(position='WRT').count() < rs.num_W_R_T:
                    roster_position = 'WRT'
                    break
            elif player.position == 'WR':
                if roster_players.filter(position=RosterPlayer.W).count() < rs.num_W:
                    roster_position = 'W'
                    break
                elif roster_players.filter(position='WT').count() < rs.num_W_R:
                    roster_position = 'WT'
                    break
                elif roster_players.filter(position='WR').count() < rs.num_W_R:
                    roster_position = 'WR'
                    break
                elif roster_players.filter(position='WRT').count() < rs.num_W_R:
                    roster_position = 'WRT'
                    break
            elif player.position == 'TE':
                if roster_players.filter(position='T').count() < rs.num_T:
                    roster_position = 'T'
                    break
                elif roster_players.filter(position='WT').count() < rs.num_W_T:
                    roster_position='WT'
                    break
                elif roster_players.filter(position='WRT').count() < rs.num_W_T:
                    roster_position='WRT'
                    break
            elif player.position == 'K':
                if roster_players.filter(position='K').count() < rs.num_K:
                    roster_position='K'
                    break
            elif player.position =='DEF':
                if roster_players.filter(position='D').count() < rs.num_D:
                    roster_position='D'
                    break
    return player, roster_position
    

@login_required
def create_league(request):
    gm = request.user.generalmanager_set.all()[0]
    form = LeagueForm()
    join_form = JoinLeagueForm()

    if request.method == 'POST':
        if 'create_league' in request.POST:
            form = LeagueForm(request.POST)
            if form.is_valid():
                league = form.save(commit=False)
                exists = True
                while exists:
                    lid = random.randint(0,999999)
                    try:
                        p = League.objects.get(lid=lid)
                    except ObjectDoesNotExist:
                        exists = False
                league.lid = lid
                league.commissioner=gm

                rs = RosterSettings.objects.create(num_Q=1,
                                                   num_R=2,
                                                   num_W=2,
                                                   num_T=1,
                                                   num_W_R_T=1
                                                   )
                league.roster_settings = rs
                ss = ScoringSettings.objects.create()
                league.scoring_settings = ss
                week = Week.objects.get(num=settings.CURRENT_WEEK)
                league.save()
                league_week = LeagueWeek.objects.create(league=league,
                                                        week=week,
                                                        status = LeagueWeek.PREDRAFT)
                league.current_week = league_week
                league.save()
                create_league_team(gm, league)
                return redirect('team_home', lid=league.lid)
        elif 'join_league' in request.POST:
            join_form = JoinLeagueForm(request.POST)
            if join_form.is_valid():
                lid = join_form.cleaned_data['lid']
                exists = True
                try:
                    league = League.objects.get(lid=lid)
                except ObjectDoesNotExist:
                    exists = False
                if exists:
                    create_league_team(gm, league)
                    return redirect('team_home', lid=league.lid)
                
    
    return render_to_response("league/create_league.html", 
                              {'form':form,
                               'join_form':join_form},
                              context_instance=RequestContext(request))

def create_league_team(gm, league):
    lteam, created = LeagueTeam.objects.get_or_create(league=league,gm=gm)

@login_required
def gm_rank(request):
    try:
        gm = GeneralManager.objects.get(user=request.user.id)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'POST' and request.is_ajax:
        reset = request.POST.get("reset", False)
        if reset:
            predraft_picks = gm.predraftpick_set.all()
            predraft_picks.update(exclude=False)
            return HttpResponse('ok')

        ranking_list = request.POST.getlist("ranking_list[]")
        exclude_list = request.POST.getlist("exclude_list[]")
        
        gm.set_predraftpick_order(ranking_list)
        ranking_picks = PredraftPick.objects.filter(gm=gm, player__id__in=ranking_list)
        ranking_picks.update(exclude=False)
        
        exclude_picks = PredraftPick.objects.filter(gm=gm, player__id__in=exclude_list)
        exclude_picks.update(exclude=True)
        return HttpResponse('ok')
    
    init_predraft_list(gm)
    predraft_picks = gm.predraftpick_set.filter(exclude=False)
    exclude_picks = gm.predraftpick_set.filter(exclude=True)
    #csrf_token = csrf(request)
    return render_to_response('league/gm_rank.html',
                              {'gm':gm,
                               'predraft_picks':predraft_picks,
                               'exclude_picks':exclude_picks,
                               },
                              context_instance=RequestContext(request))

@login_required
def team_home(request, lid):
    try:
        league = League.objects.get(lid=lid)
        gm = GeneralManager.objects.get(user=request.user.id)
        lteam = LeagueTeam.objects.get(gm=gm,league=league)
    except ObjectDoesNotExist:
        raise Http404

    if lteam.roster == None:
        roster_players = None
    else:
        roster_players = lteam.roster.rosterplayer_set.all()

    roster_players_and_stats = []
    if roster_players != None:
        games = Game.objects.all()
        ord_roster_players = []
        ord_roster_players += roster_players.filter(position=RosterPlayer.Q)
        ord_roster_players += roster_players.filter(position=RosterPlayer.R)
        ord_roster_players += roster_players.filter(position=RosterPlayer.W)
        ord_roster_players += roster_players.filter(position=RosterPlayer.T)
        ord_roster_players += roster_players.filter(position=RosterPlayer.K)
        ord_roster_players += roster_players.filter(position=RosterPlayer.D)
        ord_roster_players += roster_players.filter(position=RosterPlayer.WT)
        ord_roster_players += roster_players.filter(position=RosterPlayer.WR)
        ord_roster_players += roster_players.filter(position=RosterPlayer.WRT)
        for rplayer in ord_roster_players:
            try:
                pgs = PlayerGameStats.objects.get(player=rplayer.player,game__in=games)
            except:
                pgs = PlayerGameStats()
            roster_players_and_stats.append((rplayer, pgs))

    return render_to_response(
        'league/team_home.html',
        {'gm':gm,
         'league':league,
         'lteam':lteam,
         'roster_players_and_stats':roster_players_and_stats
         },
        context_instance=RequestContext(request))


@login_required
def create_gm(request):
    try:
        gm = GeneralManager.objects.get(user=request.user)
        exists = True
    except ObjectDoesNotExist:
        gm = None
        exists = False

    if request.method == 'POST':
        if gm == None:
            form = GeneralManagerForm(request.POST)
        else:
            form = GeneralManagerForm(request.POST, instance=gm)
        if form.is_valid():
            gm = form.save(commit=False)
            gm.user = request.user
            gm.save()
            if not exists:
                init_predraft_list(gm)
            return redirect('gm_home')
    else:
        if gm == None:
            form = GeneralManagerForm()
        else:
            form = GeneralManagerForm(instance=gm)
    
    return render_to_response('league/create_gm.html',
                              {'form':form},
                              context_instance=RequestContext(request))

def init_predraft_list(gm):
    players = Player.objects.all()
    
    for player in players:
        ppick = PredraftPick.objects.get_or_create(gm=gm, player=player)


