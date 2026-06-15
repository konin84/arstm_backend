from django.urls import path
from .views import (
    EventActiveListView,
    EventDetailView,
    ActiveBannerListView,
    track_banner_click,
    CompetitionAlertSubscribeView,
    NewsPostListView,
    NewsPostDetailView,
)

urlpatterns = [
    # Agenda
    path('agenda/', EventActiveListView.as_view(), name='event_list'),
    path('agenda/<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    
    # Bannières publicitaires (DCM)
    path('banners/', ActiveBannerListView.as_view(), name='active_banners'),
    path('banners/<int:banner_id>/click/', track_banner_click, name='track_banner_click'),
    
    # Alertes Concours
    path('subscribe-competition-alert/', CompetitionAlertSubscribeView.as_view(), name='subscribe_alert'),

    # Actualités et revue de presse
    path('news/', NewsPostListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', NewsPostDetailView.as_view(), name='news_detail'),
]