from django.urls import path, include
from build import views

urlpatterns = [
    path('', views.all_builds, name='all_builds'),
    path('filter/', views.all_builds_filter, name='all_builds_filter'),
]
