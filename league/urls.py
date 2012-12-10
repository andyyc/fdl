from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(?P<lid>\d+)/$', "league.views.league_home", name='league_home'),
    url(r'^(?P<lid>\d+)/draft/$', "league.views.draft_league", name='draft_league'),
    url(r'^enter/$', "league.views.create_league", name='create_league'),
    url(r'^rank/$', "league.views.gm_rank", name='gm_rank'),
    url(r'^(?P<lid>\d+)/team/$', "league.views.team_home", name='team_home'),
    url(r'^(?P<lid>\d+)/chat/$', "chat.views.league_chat", name='league_chat'),
    url(r'^register/$', "league.views.create_gm", name='create_gm'),
)
