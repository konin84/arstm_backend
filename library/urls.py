# apps/library/urls.py
from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    ResearchPaperListView, ResearchPaperDetailView, track_paper_download,
    SectorWatchListView, SectorWatchDetailView,
)

urlpatterns = [
    # Catégories de veille
    path('categories/', CategoryListCreateView.as_view(), name='library_category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='library_category_detail'),

    # Espace Recherche / CREMPOL
    path('papers/', ResearchPaperListView.as_view(), name='paper_list'),
    path('papers/<slug:slug>/', ResearchPaperDetailView.as_view(), name='paper_detail'),
    path('papers/<int:paper_id>/download/', track_paper_download, name='track_paper_download'),

    # Veille sectorielle
    path('watch/', SectorWatchListView.as_view(), name='sector_watch_list'),
    path('watch/<slug:slug>/', SectorWatchDetailView.as_view(), name='sector_watch_detail'),
]