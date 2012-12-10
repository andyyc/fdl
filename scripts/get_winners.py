#!/usr/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
from bloop import settings
from django.core.management import setup_environ
setup_environ(settings)
from league.models import League, LeagueWeek
from stats.models import Week
from libs.win_bot import WinBot


weeknum = settings.CURRENT_WEEK
week = Week.objects.filter(num=weeknum)
league_weeks = LeagueWeek.objects.filter(week=week)
winbot = WinBot()

for league_week in league_weeks:
    winbot.determine_winner(league_week.league)

