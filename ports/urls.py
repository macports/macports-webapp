from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index),
    path('ajax-call/summary/', views.portdetail_summary),
    path('ajax-call/builds/', views.portdetail_build_information),
    path('ajax-call/stats/', views.portdetail_stats),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/$', views.portdetail, name='port_detail'),
]
