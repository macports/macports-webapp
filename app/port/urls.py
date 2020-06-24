from django.urls import path
from django.conf.urls import url
from rest_framework import routers
from django.views.generic.base import RedirectView

from port import views

router = routers.DefaultRouter()
router.register("autocomplete/port", views.PortAutocompleteView, basename="autocomplete_port")
router.register('ports', views.PortAPIView, basename="port")

urlpatterns = [
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/builds/$', views.port_detail_build_information, name='port_builds'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/stats/$', views.port_detail_stats, name='port_stats'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/tickets/$', views.port_detail_tickets, name='port_tickets'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/$', views.port_detail, name='port_detail'),

    # redirect for the old summary url
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/summary/$', RedirectView.as_view(pattern_name='port_detail'), name='port_summary'),
]
