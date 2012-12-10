import sys, os
sys.path.append(os.path.abspath('..'))

from league.models import League, LeagueWeek

class WinBot:
    def determine_winner(self, league):
        league_week = league.current_week
        weekly_rosters = league_week.weeklyroster_set.all()
        winner = weekly_rosters[0].league_team
        winner_score = winner.roster.get_fan_pts()

        for roster in weekly_rosters:
            curr_score = roster.get_fan_pts()
            if curr_score > winner_score:
                winner = roster.league_team
                winner_score = curr_score

        league_week.winner = winner
        league_week.status = LeagueWeek.END
        league_week.save()

