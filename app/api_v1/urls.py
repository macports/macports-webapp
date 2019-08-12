from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/info/$', views.api_port_info, name='api_port_info'),
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/builds/$', views.api_port_builds, name='api_port_builds'),
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/health/$', views.api_port_health, name='api_port_health'),
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/stats/$', views.api_port_stats, name='api_port_stats'),
    url(r'^ports/$', views.api_ports_filter, name='api_ports_filter'),
    url(r'^builds/$', views.api_builds_filter, name='api_builds_filter'),
    url(r'^stats/general/$', views.api_stats_general, name='api_stats_general'),
    url(r'^stats/system/$', views.api_stats_system, name='api_stats_system'),
]
