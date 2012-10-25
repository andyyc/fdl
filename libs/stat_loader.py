import sys, os
sys.path.append(os.path.abspath('..'))

import psycopg2
import csv
from stats.models import Player, Team
#from stats.models import SeasonBasicStats, PlayerSeasonBasicStats

class StatLoader:
    def __init__(self, host, user, passwd, db):
        self.host=host
        self.user=user
        self.passwd=passwd
        self.db=db
    
    def load_file(self, filename):
        """
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (self.host, self.db, self.user, self.passwd)
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        row = cursor.fetchone()
        print "server version: ", row[0]
        cursor.close()
        conn.close()
        """
        f = open(filename, 'rU')
        reader = csv.reader(f)
        rownum = 0
        for row in reader:
            if rownum > 1:
                csv_full_name = row[1]
                csv_age = row[3]
                csv_team = row[2]
                csv_pos = row[17]
                team, tcreated = Team.objects.get_or_create(name=csv_team)
                if tcreated:
                    print team
                player, pcreated = Player.objects.get_or_create(full_name=csv_full_name, 
                                                      position=csv_pos,
                                                      age=csv_age,
                                                      team=team)
                if pcreated:
                    print player

            rownum += 1
            

        f.close()

