from django.urls import path
from django.conf.urls import url
from rest_framework import routers

from port import views
from port.views import PortInfoView

router = routers.DefaultRouter()
router.register('ports', PortInfoView, basename="port")

urlpatterns = [
    path('ajax-call/summary/', views.port_detail_summary, name='port_detail_summary_ajax'),
    path('ajax-call/builds/', views.port_detail_build_information, name='port_detail_builds_ajax'),
    path('ajax-call/stats/', views.port_detail_stats, name='port_detail_stats_ajax'),
    path('ajax-call/tickets/', views.port_detail_tickets, name='port_detail_stats_ajax'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/$', views.port_detail, name='port_detail'),
    url(r'^(?P<name>[-a-zA-Z0-9_.]+)/(?P<slug>[a-zA-z]+)/$', views.port_detail, name='port_detail_tabbed'),
]
