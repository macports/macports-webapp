from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^port/(?P<portname>[-a-zA-Z0-9_.]+)/builds$', views.fetch_port_build_history, name='fetch_port_build_history'),
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/$', views.fetch_port, name='fetch_port_detail'),
]
