from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('api/analytics/', views.analytics_data, name='analytics-data'),
    path('api/settings/', views.settings_view, name='settings'),
    path('api/system-info/', views.system_info, name='system-info'),
] 