from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^login/', 'auth.views.login', name='login'),
    url(r'^logout/', 'auth.views.logout_view', name='logout'),
)
