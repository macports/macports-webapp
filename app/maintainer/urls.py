from django.conf.urls import url
from django.urls import path
from rest_framework import routers

from maintainer import views

router = routers.DefaultRouter()
router.register("autocomplete/maintainer", views.MaintainerAutocompleteView, basename="maintainer_autocomplete")
router.register('maintainers', views.MaintainerView, basename='maintainers')

urlpatterns = [
    url(r'^(?P<m>[-a-zA-Z0-9_.]+)/$', views.maintainer, name='maintainer'),
]
