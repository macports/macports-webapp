from django.urls import path
from rest_framework import routers

from category import views

router = routers.DefaultRouter()
router.register('categories', views.CategoriesListView, basename='categories')


urlpatterns = [
    path('c/<slug:cat>/', views.category, name='category'),
    path('search/', views.search_ports_in_category, name='search_in_category')
]
