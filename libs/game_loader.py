import sys, os
sys.path.append(os.path.abspath('..'))

import psycopg2
import csv
from stats.models import PlayerGameStats, Game, Team, Player
from datetime import datetime
import urllib2
from bs4 import BeautifulSoup, NavigableString

class GameLoader:
    GAME_DATA_URL = "http://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min=2012&year_max=2012&season_start=1&season_end=-1&age_min=0&age_max=99&league_id=NFL&team_id=&opp_id=&game_type=R&game_num_min=0&game_num_max=99&week_num_min=%d&week_num_max=%d&game_day_of_week=&game_location=&game_result=&is_active=&is_hof=&c1stat=pass_cmp&c1comp=gt&c1val=&c2stat=rush_att&c2comp=gt&c2val=&c3stat=rec&c3comp=gt&c3val=&c4stat=all_td&c4comp=gt&c4val=&order_by=all_td&offset=%d"

    HEADER_MAP = {
        "full_name":1,
        "game_date":3,
        "team1":5,
        "team2_is_home":6,
        "team2":7,
        "week":10,
        "pass_cmp":12,
        "pass_att":13,
        "pass_yds":15,
        "pass_td":16,
        "pass_int":17,
        "rush_att":21,
        "rush_yds":22,
        "rush_td":24,
        "rec_rec":25,
        "rec_yds":26,
        "rec_td":28,
        "two_pt":36
        }

    def __init__(self):
        pass
    
    def read_url(self, week=1, offset=0):
        f = urllib2.urlopen(self.GAME_DATA_URL % (week, week, offset))
        return f.read()

    def load(self, week=1, offset=0):
        data = self.read_url(week, offset)
        soup = BeautifulSoup(data)
        tag = soup.find(id="stats")
        if tag == None:
            return 0
        count = 0
        for row in tag.tbody.find_all("tr"):
            classes = row['class']
            try:
                classes.index('thead')
                continue
            except:
                pass
            count += 1
            tds = row.find_all('td')
            full_name = str(tds[self.HEADER_MAP['full_name']].string)  
            game_date = str(tds[self.HEADER_MAP['game_date']].string)
            team1 = str(tds[self.HEADER_MAP['team1']].string)
            team2_is_home = str(tds[self.HEADER_MAP['team2_is_home']].string)
            team2 = str(tds[self.HEADER_MAP['team2']].string)
            week = str(tds[self.HEADER_MAP['week']].string)
            pass_cmp = str(tds[self.HEADER_MAP['pass_cmp']].string)  
            pass_att = str(tds[self.HEADER_MAP['pass_att']].string)  
            pass_yds = str(tds[self.HEADER_MAP['pass_yds']].string)
            pass_td = str(tds[self.HEADER_MAP['pass_td']].string)
            pass_int = str(tds[self.HEADER_MAP['pass_int']].string)  
            rush_att = str(tds[self.HEADER_MAP['rush_att']].string)  
            rush_yds = str(tds[self.HEADER_MAP['rush_yds']].string)
            rush_td = str(tds[self.HEADER_MAP['rush_td']].string)  
            rec_rec = str(tds[self.HEADER_MAP['rec_rec']].string)   
            rec_yds = str(tds[self.HEADER_MAP['rec_yds']].string)
            rec_td = str(tds[self.HEADER_MAP['rec_td']].string)  
            two_pt = str(tds[self.HEADER_MAP['two_pt']].string)
            team1, t1created = Team.objects.get_or_create(name=team1)
            team2, t2created = Team.objects.get_or_create(name=team2)
            try:
                player = Player.objects.get(full_name=full_name, team=team1)
            except:
                print full_name + " does not exist"
                continue
            print full_name
            if team2_is_home == '@':
                home_team = team2
                away_team = team1
            else:
                home_team = team1
                away_team = team2

            game_date = datetime.strptime(game_date, "%Y-%m-%d")
            game, gcreated = Game.objects.get_or_create(week=week,
                                              datetime=game_date,
                                              away_team=away_team,
                                              home_team=home_team)

            pgs, pcreated = PlayerGameStats.objects.get_or_create(player=player,
                                                                  game=game)
            pgs.pass_cmp = pass_cmp
            pgs.pass_att = pass_att
            pgs.pass_yds = pass_yds
            pgs.pass_td = pass_td
            pgs.pass_int = pass_int
            pgs.rush_att = rush_att
            pgs.rush_yds = rush_yds
            pgs.rush_td = rush_td
            pgs.rec_rec = rec_rec
            pgs.rec_yds = rec_yds
            pgs.rec_td = rec_td
            pgs.two_pt = two_pt if two_pt != "None" else 0
            pgs.save()
            
        return count
        
"""    
    def load_file(self, offset):
        f = open(filename, 'rU')
        reader = csv.reader(f)

        game, gcreated = Game.objects.get_or_create(week=1,
                                                    datetime=datetime.now(),
                                                    away_team=Team.objects.get(name="CIN"),
                                                    home_team=Team.objects.get(name="CLE"))
        for row in reader:
            if row[0] == '':
                continue

            full_name = row[0]
            team_name = row[1]

            try:
                team = Team.objects.get(name=team_name)
                player = Player.objects.get(full_name=full_name,team=team)
            except:
                continue

            for i in xrange(2, len(row)):
                if row[i] == '':
                    row[i] = 0
            passing_cmp = row[2]
            passing_att = row[3]
            passing_yds = row[4]
            passing_td = row[5]
            passing_int = row[6]
            rushing_att = row[8]
            rushing_yds = row[9]
            rushing_td = row[10]
            receiving_rec = row[12]
            receiving_yds = row[13]
            receiving_td = row[14]
            
            pgs, pcreated = PlayerGameStats.objects.get_or_create(player=player,
                                                                  game=game)
            pgs.pass_cmp = passing_cmp
            pgs.pass_att = passing_att
            pgs.pass_yds = passing_yds
            pgs.pass_td = passing_td
            pgs.pass_int = passing_int
            pgs.rec_rec = receiving_rec
            pgs.rec_yds = receiving_yds
            pgs.rec_td = receiving_td
            pgs.rush_att = rushing_att
            pgs.rush_yds = rushing_yds
            pgs.rush_td = rushing_td
            pgs.save()
        f.close()

"""
