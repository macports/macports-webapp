from django.urls import path
from rest_framework import routers

from buildhistory import views

router = routers.DefaultRouter()
router.register('builders', views.BuilderAPIView, basename='builders')
router.register('builds', views.BuildHistoryAPIView, basename='builds')
router.register('files', views.InstalledFilesAPIView, basename='files')

urlpatterns = [
    path('', views.all_builds, name='all_builds'),
    path('buildbot2/submit', views.buildbot2_submit, name='buildbot2_submit')
]
