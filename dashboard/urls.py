from django.urls import path
from django.shortcuts import redirect
from . import views

def admin_redirect(request):
    return redirect('/admin/')

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('admin/', admin_redirect, name='dashboard-admin-redirect'),
    path('user-registrations/', views.user_registrations_view, name='user-registrations'),
    path('api/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('api/analytics/', views.analytics_data, name='analytics-data'),
    path('api/settings/', views.settings_view, name='settings'),
    path('api/system-info/', views.system_info, name='system-info'),
    path('api/transaction/<int:transaction_id>/', views.transaction_details, name='transaction-details'),
    path('api/activity/', views.activity_feed, name='activity-feed'),
] 