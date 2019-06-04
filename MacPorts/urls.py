"""MacPorts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from ports import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='Home'),
    path('statistics/submit/', views.stats_submit, name='stats_submit'),
    path('statistics/', views.stats, name='stats_home'),
    url(r'^statistics/port/(?P<name>[-a-zA-Z0-9_.]+)/$', views.stats_portdetail, name='stats_portdetail'),
    url(r'^maintainer/github/(?P<github_handle>[-a-zA-Z0-9_.]+)/$', views.maintainer_detail_github, name='maintainer_detail_github'),
    url(r'^maintainer/email/(?P<name>[-a-zA-Z0-9_.]+)__(?P<domain>[-a-zA-Z0-9_.]+)/$', views.maintainer_detail_email, name='maintainer_detail_email'),
    path('ports/', include('ports.urls'), name='Ports-Index'),
    path('all_builds/filter/', views.all_builds_filter),
    path('all_builds/', views.all_builds_view, name='all_builds'),
    path('update/', views.update_api, name='update_api')
]
