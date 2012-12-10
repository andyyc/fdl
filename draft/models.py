from django.db import models
from stats.models import Player
from league.models import League, LeagueTeam, LeagueWeek

class Draft(models.Model):
    league_week = models.OneToOneField(LeagueWeek)
    current_round = models.PositiveIntegerField()
    current_pick_num = models.PositiveIntegerField()
    picks = models.ManyToManyField(Player, through="Pick")
    league_teams = models.ManyToManyField(LeagueTeam, through="DraftOrder")

class DraftOrder(models.Model):
    draft = models.ForeignKey(Draft)
    league_team = models.ForeignKey(LeagueTeam)
    class Meta:
        order_with_respect_to = 'draft'
    
class Pick(models.Model):
    num = models.PositiveSmallIntegerField()
    draft_round = models.PositiveSmallIntegerField()
    draft = models.ForeignKey(Draft)
    player = models.ForeignKey(Player)
    league_team = models.ForeignKey(LeagueTeam)
