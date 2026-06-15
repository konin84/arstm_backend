from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Domain, Program, Document
from .serializers import (
    DomainSerializer,
    ProgramListSerializer, ProgramDetailSerializer, ProgramWriteSerializer,
    DocumentSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Lecture publique, écriture réservée aux admins (is_staff)."""
    def has_permission(self, request, _view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# ─── Domains ──────────────────────────────────────────────────────────────────

class DomainListView(generics.ListCreateAPIView):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAdminOrReadOnly]


class DomainDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# ─── Programs ─────────────────────────────────────────────────────────────────

class ProgramListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProgramWriteSerializer
        return ProgramListSerializer

    def get_queryset(self):
        # Admins see all programs; public only sees active ones
        queryset = Program.objects.all() if (
            self.request.user.is_authenticated and self.request.user.is_staff
        ) else Program.objects.filter(is_active=True)

        program_type = self.request.query_params.get('type')
        domain_slug = self.request.query_params.get('domain')
        regime = self.request.query_params.get('regime')

        if program_type:
            queryset = queryset.filter(program_type=program_type)
        if domain_slug:
            queryset = queryset.filter(domain__slug=domain_slug)
        if regime:
            queryset = queryset.filter(regime=regime)

        return queryset


class ProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProgramWriteSerializer
        return ProgramDetailSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Program.objects.all()
        return Program.objects.filter(is_active=True)


# ─── Documents ────────────────────────────────────────────────────────────────

class DocumentListView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrReadOnly]


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrReadOnly]


@api_view(['POST'])
def track_document_download(request, document_id):
    """Enregistre un téléchargement et retourne le compteur mis à jour."""
    document = get_object_or_404(Document, id=document_id)
    document.download_count += 1
    document.save()
    return Response(
        {'status': 'success', 'download_count': document.download_count},
        status=status.HTTP_200_OK,
    )
