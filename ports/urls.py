from django.urls import path , include
from . import views
from django.conf.urls import url


urlpatterns = [
    path('', views.index),
    path('search/', views.search, name='ports_search'),
    path('filter/', views.category_filter, name='category_filter'),
    path('load_tickets/', views.tickets, name='trac_tickets'),
    path('statistics/', views.stats, name='stats_home'),
    path('category/<slug:cat>', views.categorylist, name='category_list'),
    path('sort-by-letter/<slug:letter>', views.letterlist, name='letter_list'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/$', views.portdetail, name='port_detail'),
]