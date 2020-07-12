from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin
from haystack.views import FacetedSearchView
from haystack.query import SearchQuerySet
from rest_framework.routers import DefaultRouter
from django.views.generic.base import RedirectView
import notifications.urls

import views
from port.views import SearchAPIView
from port.forms import AdvancedSearchForm
from port.urls import router as port_router
from category.urls import router as category_router
from buildhistory.urls import router as buildhistory_router
from maintainer.urls import router as maintainer_router
from variant.urls import router as variants_router
from stats.views import PortStatisticsAPIView, PortMonthlyInstallationsAPIView, GeneralStatisticsAPIView

# Router for rest framework
router = DefaultRouter()
router.register('search', SearchAPIView, basename='search')
router.registry.extend(port_router.registry)
router.registry.extend(category_router.registry)
router.registry.extend(buildhistory_router.registry)
router.registry.extend(maintainer_router.registry)
router.registry.extend(variants_router.registry)

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
    path('maintainer/', include('maintainer.urls')),
    path('port/', include('port.urls')),
    url(r"api/v1/statistics/port/monthly", PortMonthlyInstallationsAPIView.as_view(), name='port-monthly-stats'),
    url(r"api/v1/statistics/port", PortStatisticsAPIView.as_view(), name='port-stats'),
    url(r"api/v1/statistics/", GeneralStatisticsAPIView.as_view(), name='general-stats'),
    url(r"api/v1/", include(router.urls)),
    path('category/', include('category.urls')),
    path('variant/', include('variant.urls')),
    path('ports/search/', views.search, name='ports_search'),
    path('all_builds/', include('buildhistory.urls')),
    path('about/', views.about_page, name='about_page'),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('user.urls')),
    url('^accounts/notifications/', include(notifications.urls, namespace='notifications')),

    # redirects to keep the old urls alive
    url(r'^maintainer/github/(?P<m>[-a-zA-Z0-9_.]+)/$', RedirectView.as_view(pattern_name='maintainer'), name='maintainer_old'),
    url(r'^ports/category/(?P<cat>[-a-zA-Z0-9_.]+)/$', RedirectView.as_view(pattern_name='category'), name='category_old'),
    url(r'^ports/variant/(?P<v>[-a-zA-Z0-9_.]+)/$', RedirectView.as_view(pattern_name='variant'), name='variant_old'),
    url(r'^ports/all_builds/$', RedirectView.as_view(pattern_name='all_builds'), name='all_build_old'),
]
