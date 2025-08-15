from django.urls import re_path
from rest_framework import routers

from maintainer import views

router = routers.DefaultRouter()
router.register("autocomplete/maintainer", views.MaintainerAutocompleteView, basename="maintainer_autocomplete")
router.register('maintainer', views.MaintainerAPIView, basename='maintainer')

urlpatterns = [
    re_path(r'^(?P<m>[-a-zA-Z0-9_.]+)/$', views.maintainer, name='maintainer'),
]
