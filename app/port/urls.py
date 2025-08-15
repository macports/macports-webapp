from django.urls import re_path
from rest_framework import routers
from django.views.generic.base import RedirectView

from port import views

router = routers.DefaultRouter()
router.register("autocomplete/port", views.PortAutocompleteView, basename="autocomplete_port")
router.register('ports', views.PortAPIView, basename="port")

urlpatterns = [
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/details/$', views.port_details, name='port_details'),
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/builds/$', views.port_builds, name='port_builds'),
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/stats/$', views.port_stats, name='port_stats'),
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/tickets/$', views.port_tickets, name='port_tickets'),
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/health/$', views.port_health, name='port_health'),
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/follow/$', views.follow_port, name='follow_port'),
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/unfollow/$', views.unfollow_port, name='unfollow_port'),
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/default_page_toggle/$', views.default_port_page_toggle, name='default_port_page_toggle'),

    # Main port landing page- if the "default_port_page" cookie is set to summary
    # then this automatically redirects to 'port_details' url
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/$', views.port_landing, name='port_detail'),

    # redirect for old summary url
    re_path(r'^(?P<name>[-a-zA-Z0-9_.]+)/summary/$', RedirectView.as_view(pattern_name='port_details'), name='port_summary'),
]
