from django.conf.urls import url
from django.urls import path
from rest_framework import routers

from maintainer import views

router = routers.DefaultRouter()
router.register('maintainers', views.MaintainerView, basename='maintainers')

urlpatterns = [
    url(r'^github/(?P<github_handle>[-a-zA-Z0-9_.]+)/$', views.maintainer_detail_github, name='maintainer_detail_github'),
    url(r'^email/(?P<name>[-a-zA-Z0-9_.]+)__(?P<domain>[-a-zA-Z0-9_.]+)/$', views.maintainer_detail_email, name='maintainer_detail_email'),
    path('search/', views.search_ports_in_maintainer, name='search_in_maintainer')
]
