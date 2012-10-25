from django.db import models

class Player(models.Model):
    POSITION_CHOICES = (
        ('QB', 'Quarterback'),
        ('RB', 'Running back'),
        ('WR', 'Wide receiver'),
        ('TE', 'Tight end'),
        ('K', 'Kicker'),
        ('DEF', 'Defense')
        ) 
    
    full_name = models.CharField(max_length=64)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    age = models.PositiveSmallIntegerField()
    team = models.ForeignKey('Team')

class Team(models.Model):
    TEAM_CHOICES = (
        ('ARI', 'Arizona Cardinals'),
        ('ATL', 'Atlanta Falcons'),
        ('BAL', 'Baltimore Ravens')
    )
    TEAM_MAP = {
        'Arizona Cardinals':'ARI',
        'Atlanta Falcons':'ATL',
        'Baltimore Ravens':'BAL',
        'Buffalo Bills':'BUF',
        'Carolina Panthers':'CAR',
        'Chicago Bears':'CHI',
        'Cincinnati Bengals':'CIN',
        'Cleveland Browns':'CLE',
        'Dallas Cowboys':'DAL',
        'Denver Broncos':'DEN',
        'Detroit Lions':'DET',
        'Green Bay Packers':'GNB',
        'Houston Texans':'HOU',
        'Indianapolis Colts':'IND',
        'Jacksonville Jaguars':'JAX',
        'Kansas City Chiefs':'KAN',
        'Miami Dolphins':'MIA',
        'Minnesota Vikings':'MIN',
        'New Orleans Saints':'NOR',
        'New England Patriots':'NWE',
        'New York Giants':'NYG',
        'New York Jets':'NYJ',
        'Oakland Raiders':'OAK',
        'Philadelphia Eagles':'PHI',
        'Pittsburgh Steelers':'PIT',
        'San Diego Chargers':'SDG',
        'San Francisco 49ers':'SFO',
        'Seattle Seahawks':'SEA',
        'St. Louis Rams':'STL',
        'Tampa Bay Buccaneers':'TAM',
        'Tennessee Titans':'TEN',
        'Washington Redskins':'WAS',
    }
    name = models.CharField(max_length=3, choices=TEAM_CHOICES, unique=True)

class PlayerStats(models.Model):
    pass_cmp = models.PositiveSmallIntegerField(default=0)
    pass_att = models.PositiveSmallIntegerField(default=0)
    pass_yds = models.SmallIntegerField(default=0)
    pass_td = models.PositiveSmallIntegerField(default=0)
    pass_int = models.PositiveSmallIntegerField(default=0)
    rec_rec = models.PositiveSmallIntegerField(default=0)
    rec_yds = models.SmallIntegerField(default=0)
    rec_td = models.PositiveSmallIntegerField(default=0)
    rush_att = models.PositiveSmallIntegerField(default=0)
    rush_yds = models.SmallIntegerField(default=0)
    rush_td = models.PositiveSmallIntegerField(default=0)   
    two_pt = models.PositiveSmallIntegerField(default=0)
    fl = models.PositiveSmallIntegerField(default=0)
    class Meta:
        abstract = True

class PlayerSeasonStats(PlayerStats):
    player = models.ForeignKey(Player)
    year = models.PositiveSmallIntegerField()

"""
class PlayerSeasonStats(models.Model):
    player = models.ForeignKey(Player)
    season = models.PositiveSmallIntegerField()
    offensive_stats = models.OneToOneField('OffensiveStats', null=True)
    #kicking_stats = models.OneToOneField('KickingStats')
    #defensive_stats = models.OneToOneField('DefensiveStats')
"""

class PlayerGameStats(PlayerStats):
    player = models.ForeignKey(Player)
    game = models.ForeignKey('Game')
    
    
class Game(models.Model):
    week = models.PositiveIntegerField()
    datetime = models.DateTimeField()
    away_team = models.ForeignKey(Team, related_name="away_games")
    home_team = models.ForeignKey(Team, related_name="home_games")
