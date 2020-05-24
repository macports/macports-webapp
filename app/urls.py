from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin
from haystack.views import FacetedSearchView
from haystack.query import SearchQuerySet
from rest_framework import routers

import views
from port.forms import AdvancedSearchForm
from port.views import PortSearchView
from port.urls import router as port_router
from category.urls import router as category_router
from buildhistory.urls import router as buildhistory_router
from maintainer.urls import router as maintainer_router

# Router for rest framework
router = routers.DefaultRouter()
router.register("search", PortSearchView, basename="ports_advanced_search")
router.registry.extend(port_router.registry)
router.registry.extend(category_router.registry)
router.registry.extend(buildhistory_router.registry)
router.registry.extend(maintainer_router.registry)

urlpatterns = [
    path('', views.index, name='home'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    # URL for advanced search page
    url(r'^search/', FacetedSearchView(
        form_class=AdvancedSearchForm,
        searchqueryset=SearchQuerySet().facet('maintainers').facet('categories').facet('variants'),
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
