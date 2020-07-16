from django.conf.urls import url
from rest_framework import routers
from django.views.generic.base import RedirectView

from port import views

router = routers.DefaultRouter()
router.register("autocomplete/port", views.PortAutocompleteView, basename="autocomplete_port")
router.register('ports', views.PortAPIView, basename="port")

urlpatterns = [
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/details/$', views.port_details, name='port_details'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/builds/$', views.port_builds, name='port_builds'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/stats/$', views.port_stats, name='port_stats'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/tickets/$', views.port_tickets, name='port_tickets'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/follow/$', views.follow_port, name='follow_port'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/unfollow/$', views.unfollow_port, name='unfollow_port'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/default_page_toggle/$', views.default_port_page_toggle, name='default_port_page_toggle'),

    # Main port landing page- if the "default_port_page" cookie is set to summary
    # then this automatically redirects to 'port_details' url
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/$', views.port_landing, name='port_detail'),

    # redirect for old summary url
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/summary/$', RedirectView.as_view(pattern_name='port_details'), name='port_summary'),
]
