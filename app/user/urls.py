from django.urls import path, include
from django.conf.urls import url

from user import views

urlpatterns = [
    path('profile/', views.profile, name='account_profile')
]
