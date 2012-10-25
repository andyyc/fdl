#!/usr/bin/env python
# Run this with
# PYTHONPATH=. DJANGO_SETTINGS_MODULE=testsite.settings testsite/tornado_main.py
# Serves by default at
# http://localhost:8080/hello-tornado and
# http://localhost:8080/hello-django
import sys
import os
sys.path.append(os.path.abspath('..'))
from bloop import settings
#from django.core.management import setup_environ
#setup_environ(settings)
from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

from chat.chatdemo import *


define('port', type=int, default=8080)
addr="0.0.0.0"

def main():
  wsgi_app = tornado.wsgi.WSGIContainer(
    django.core.handlers.wsgi.WSGIHandler())
  tornado_settings = dict(
    cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=True,
    autoescape=None,
    )

  tornado_app = tornado.web.Application([
      (r"/chat", MainHandler),
      (r"/chat/chatsocket", ChatSocketHandler),
      ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
      ], **tornado_settings)
  server = tornado.httpserver.HTTPServer(tornado_app)
  server.listen(options.port, address=addr)
  print "Started Tornado web server"
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bloop.settings")
  main()
