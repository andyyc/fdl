import sys, os
sys.path.append(os.path.abspath('..'))

import psycopg2
import csv
from stats.models import PlayerGameStats, Game, Team, Player
from datetime import datetime

class ScheduleLoader:
    def __init__(self, host, user, passwd, db):
        self.host=host
        self.user=user
        self.passwd=passwd
        self.db=db
    
    def load_file(self, filename):
        f = open(filename, 'rU')
        reader = csv.reader(f)
        for row in reader:
            try:
                int(row[0])
            except:
                continue
            week = row[0]
            date = row[2]
            away_team = row[3]
            ateam = Team.objects.get(name=Team.TEAM_MAP[away_team])
            home_team = row[5]
            hteam = Team.objects.get(name=Team.TEAM_MAP[home_team])
            time = row[6]
            year = 2012

            dt = datetime.strptime(date + " " + str(year) + " " + time, "%B %d %Y %I:%M %p")
            Game.objects.get_or_create(week=week, datetime=dt, away_team=ateam,home_team=hteam)
        f.close()

