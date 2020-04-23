from django.urls import path

from category import views


urlpatterns = [
    path('c/<slug:cat>/', views.category, name='category'),
    path('search/', views.search_ports_in_category, name='search_in_category')
]
