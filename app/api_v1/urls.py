from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/info$', views.api_port_info, name='api_port_info'),
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/builds$', views.api_port_builds, name='api_port_builds'),
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/health$', views.api_port_health, name='api_port_health'),
]
