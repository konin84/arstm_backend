from django.urls import path
from .views import (
    EventActiveListView, EventDetailView,
    ActiveBannerListView, track_banner_click,
    CompetitionAlertSubscribeView,
    CompetitionPublicListView, CompetitionPublicDetailView,
    NewsPostListView, NewsPostDetailView, NewsCategoryListView,
    EventAdminListCreateView, EventAdminDetailView,
    PromotionBannerAdminListCreateView, PromotionBannerDetailView,
    CompetitionAdminListCreateView, CompetitionAdminDetailView,
    NewsPostAdminListCreateView, NewsPostAdminDetailView,
    NewsCategoryAdminListCreateView, NewsCategoryDetailView,
)

urlpatterns = [
    # ── Lecture publique ──────────────────────────────────────────────────────
    path('agenda/', EventActiveListView.as_view(), name='event_list'),
    path('agenda/<slug:slug>/', EventDetailView.as_view(), name='event_detail'),

    path('banners/', ActiveBannerListView.as_view(), name='active_banners'),
    path('banners/<int:banner_id>/click/', track_banner_click, name='track_banner_click'),

    path('subscribe-competition-alert/', CompetitionAlertSubscribeView.as_view(), name='subscribe_alert'),

    path('competitions/', CompetitionPublicListView.as_view(), name='competition_list'),
    path('competitions/<slug:slug>/', CompetitionPublicDetailView.as_view(), name='competition_detail'),

    path('news-categories/', NewsCategoryListView.as_view(), name='news_category_list'),
    path('news/', NewsPostListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', NewsPostDetailView.as_view(), name='news_detail'),

    # ── Admin CRUD ────────────────────────────────────────────────────────────
    path('manage/events/', EventAdminListCreateView.as_view(), name='event_admin_list'),
    path('manage/events/<slug:slug>/', EventAdminDetailView.as_view(), name='event_admin_detail'),

    path('manage/banners/', PromotionBannerAdminListCreateView.as_view(), name='banner_admin_list'),
    path('manage/banners/<int:pk>/', PromotionBannerDetailView.as_view(), name='banner_admin_detail'),

    path('manage/competitions/', CompetitionAdminListCreateView.as_view(), name='competition_admin_list'),
    path('manage/competitions/<slug:slug>/', CompetitionAdminDetailView.as_view(), name='competition_admin_detail'),

    path('manage/news/', NewsPostAdminListCreateView.as_view(), name='news_admin_list'),
    path('manage/news/<slug:slug>/', NewsPostAdminDetailView.as_view(), name='news_admin_detail'),

    path('manage/news-categories/', NewsCategoryAdminListCreateView.as_view(), name='news_category_admin_list'),
    path('manage/news-categories/<str:code>/', NewsCategoryDetailView.as_view(), name='news_category_admin_detail'),
]