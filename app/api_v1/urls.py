from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('ports/count/', views.fetch_total_number_of_ports, name='fetch_total_number_of_ports'),
    path('ports/<int:page_size>/page/<int:page_num>/', views.fetch_paginated_ports, name='fetch_paginated_ports'),
    url(r'^port/(?P<portname>[-a-zA-Z0-9_.]+)/builds$', views.fetch_port_build_history, name='fetch_port_build_history'),
    url(r'^port/(?P<name>[-a-zA-Z0-9_.]+)/$', views.fetch_port, name='fetch_port_detail'),
    url(r'^category/(?P<category>[-a-zA-Z0-9_.]+)/ports/$', views.fetch_portnames_of_category, name='fetch_portnames_of_category'),
]
