from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/$', views.portdetail, name='port_detail'),
]
