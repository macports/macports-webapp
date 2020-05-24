from django.urls import path

from stats import views

urlpatterns = [
    path('', views.stats, name='stats'),
    path('submit/', views.stats_submit, name='stats_submit'),
    path('ports/', views.stats_port_installations, name='stats_port_installations'),
    path('ports/filter/', views.stats_port_installations_filter, name='stats_port_installations_filter'),
    path('faq/', views.stats_faq, name='stats_faq'),
]
