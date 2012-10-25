#!/usr/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
from bloop import settings
from django.core.management import setup_environ
setup_environ(settings)

from libs.game_loader import GameLoader

gl = GameLoader()
offset = 0
while True:
    count = gl.load(offset=offset)
    print count
    if count == 0:
        break
    offset += 100

