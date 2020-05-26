from django.urls import path
from django.conf.urls import url
from rest_framework import routers

from variant import views

router = routers.DefaultRouter()
router.register('autocomplete/variant', views.VariantAutocompleteView, basename='autocomplete_variant')

urlpatterns = [
    url(r'^v/(?P<variant>[a-zA-Z0-9_.]+)/$', views.variant, name='variant'),
    path('search/', views.search_ports_in_variant, name='search_ports_in_variant')
]
