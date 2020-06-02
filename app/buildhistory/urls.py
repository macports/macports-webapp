from django.urls import path
from rest_framework import routers

from buildhistory import views

router = routers.DefaultRouter()
router.register('builders', views.BuilderView, basename='builders')
router.register('buildhistory', views.BuildHistoryView, basename='buildhistory')
router.register('files', views.InstalledFilesView, basename='files')

urlpatterns = [
    path('', views.all_builds, name='all_builds'),
    path('filter/', views.all_builds_filter, name='all_builds_filter'),
]
