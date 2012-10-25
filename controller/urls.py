from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', "controller.views.gm_home", name='gm_home'),
)
