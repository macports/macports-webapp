from django.urls import path
from django.conf.urls import url

from variants import views

urlpatterns = [
    url(r'^v/(?P<variant>[a-zA-Z0-9_.]+)/$', views.variant, name='variant'),
    path('search/', views.search_ports_in_variant, name='search_ports_in_variant')

]
