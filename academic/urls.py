from django.urls import path
from .views import (
    DomainListView, DomainDetailView,
    ProgramListView, ProgramDetailView,
    ProgramTypeListView, ProgramTypeDetailView,
    RegimeListView, RegimeDetailView,
    DocumentListView, DocumentDetailView,
    track_document_download,
)

urlpatterns = [
    path('domains/', DomainListView.as_view(), name='domain_list'),
    path('domains/<slug:slug>/', DomainDetailView.as_view(), name='domain_detail'),

    path('program-types/', ProgramTypeListView.as_view(), name='program_type_list'),
    path('program-types/<str:code>/', ProgramTypeDetailView.as_view(), name='program_type_detail'),

    path('regimes/', RegimeListView.as_view(), name='regime_list'),
    path('regimes/<str:code>/', RegimeDetailView.as_view(), name='regime_detail'),

    path('programs/', ProgramListView.as_view(), name='program_list'),
    path('programs/<slug:slug>/', ProgramDetailView.as_view(), name='program_detail'),

    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:document_id>/download/', track_document_download, name='track_document_download'),
]