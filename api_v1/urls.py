from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/$', views.fetch_port, name='fetch_port_detail'),
]
