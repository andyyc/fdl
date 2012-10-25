#!/usr/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
from bloop import settings
from django.core.management import setup_environ
setup_environ(settings)

from libs.game_loader import GameLoader
default_db = settings.DATABASES.get('default')
host = default_db.get('HOST')
user = default_db.get('USER')
passwd = default_db.get('PASSWORD')
db = default_db.get('NAME')
gl = GameLoader(host=host,
                user=user,
                passwd=passwd,
                db=db)
gl.load_file('/home/fthd/fdl/bloop/csv/game.csv')

