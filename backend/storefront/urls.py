"""
URL configuration for storefront app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('feed/', views.live_feed_view, name='live_feed'),
    path('playground/', views.playground_view, name='playground'),
    path('history/', views.history_view, name='history'),
    path('billing/', views.billing_view, name='billing'),
    path('settings/', views.settings_view, name='settings'),
    path('support/', views.support_view, name='support'),
    path('api/v1/scan/', views.scan_api_view, name='api_scan'),
    path('api/v1/verify/', views.verify_token_api_view, name='api_verify'),
    path('api/v1/stats/', views.stats_api_view, name='api_stats'),
]
