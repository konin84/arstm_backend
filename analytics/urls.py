# apps/analytics/urls.py
from django.urls import path
from .views import TrackActionView, DCMDashboardStatsView

urlpatterns = [
    # Appel de tracking en arrière plan par React
    path('track/', TrackActionView.as_view(), name='track_action'),
    
    # Données du tableau de bord d'administration
    path('dashboard/summary/', DCMDashboardStatsView.as_view(), name='dcm_dashboard_summary'),
]