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
from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin
from haystack.views import SearchView, search_view_factory
from rest_framework import routers

import views
from port.forms import AdvancedSearchForm
from port.views import PortSearchView

# Router for rest framework
router = routers.DefaultRouter()
router.register("search", PortSearchView, basename="ports_advanced_search")

urlpatterns = [
    path('', views.index, name='home'),
    path('admin/', admin.site.urls),
    # URL for advanced search page
    url(r'^search/', search_view_factory(
        view_class=SearchView,
        form_class=AdvancedSearchForm,
        template='search/search.html',
    ), name='search'),
    path('statistics/', include('stats.urls')),
    path('maintainers/', include('maintainer.urls')),
    path('port/', include('port.urls')),
    url(r"api/v1/", include(router.urls)),
    path('categories/', include('category.urls')),
    path('variants/', include('variant.urls')),
    path('ports/search/', views.search, name='ports_search'),
    path('all_builds/', include('buildhistory.urls')),
    path('about/', views.about_page, name='about_page'),
]
