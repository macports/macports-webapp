from django.urls import re_path
from rest_framework import routers

from variant import views

router = routers.DefaultRouter()
router.register('autocomplete/variant', views.VariantAutocompleteView, basename='autocomplete_variant')

urlpatterns = [
    re_path(r'^(?P<v>[a-zA-Z0-9_.-]+)/$', views.variant, name='variant'),
]
