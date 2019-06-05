from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index),
    path('search/', views.search, name='ports_search'),
    path('filter/maintainer/', views.search_ports_in_maintainer, name='search_ports_in_maintainer'),
    path('filter/category/', views.search_ports_in_category, name='search_ports_in_category'),
    path('load_tickets/', views.tickets, name='trac_tickets'),
    path('statistics/', views.stats, name='stats_home'),
    path('category/<slug:cat>', views.categorylist, name='category_list'),
    path('variant/<slug:variant>', views.variantlist, name='variant_list'),
    path('sort-by-letter/<slug:letter>', views.letterlist, name='letter_list'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/$', views.portdetail, name='port_detail'),
]
