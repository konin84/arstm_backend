from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Domain, Program, ProgramType, Regime, Document
from .serializers import (
    DomainSerializer,
    ProgramListSerializer, ProgramDetailSerializer, ProgramWriteSerializer,
    ProgramTypeSerializer, RegimeSerializer,
    DocumentSerializer,
)
from users.permissions import IsAdminOrModeratorOrReadOnly, PRIVILEGED_ROLES


# ─── Domains ──────────────────────────────────────────────────────────────────

class DomainListView(generics.ListCreateAPIView):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class DomainDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'


# ─── Program types & régimes (listes dynamiques) ───────────────────────────────

class ProgramTypeListView(generics.ListCreateAPIView):
    """Lecture publique (actifs seulement) ; écriture réservée aux admins et modérateurs."""
    serializer_class = ProgramTypeSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or getattr(user, 'role', None) in PRIVILEGED_ROLES):
            return ProgramType.objects.all()
        return ProgramType.objects.filter(is_active=True)


class ProgramTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProgramType.objects.all()
    serializer_class = ProgramTypeSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'code'


class RegimeListView(generics.ListCreateAPIView):
    """Lecture publique (actifs seulement) ; écriture réservée aux admins et modérateurs."""
    serializer_class = RegimeSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or getattr(user, 'role', None) in PRIVILEGED_ROLES):
            return Regime.objects.all()
        return Regime.objects.filter(is_active=True)


class RegimeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Regime.objects.all()
    serializer_class = RegimeSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'code'


# ─── Programs ─────────────────────────────────────────────────────────────────

class ProgramListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProgramWriteSerializer
        return ProgramListSerializer

    def get_queryset(self):
        # Admins/moderators see all programs; public only sees active ones
        user = self.request.user
        can_see_all = user.is_authenticated and (
            user.is_staff or getattr(user, 'role', None) in PRIVILEGED_ROLES
        )
        queryset = Program.objects.all() if can_see_all else Program.objects.filter(is_active=True)

        program_type = self.request.query_params.get('type')
        domain_slug = self.request.query_params.get('domain')
        regime = self.request.query_params.get('regime')

        if program_type:
            queryset = queryset.filter(program_type__code=program_type)
        if domain_slug:
            queryset = queryset.filter(domain__slug=domain_slug)
        if regime:
            queryset = queryset.filter(regime__code=regime)

        return queryset


class ProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProgramWriteSerializer
        return ProgramDetailSerializer

    def get_queryset(self):
        user = self.request.user
        can_see_all = user.is_authenticated and (
            user.is_staff or getattr(user, 'role', None) in PRIVILEGED_ROLES
        )
        return Program.objects.all() if can_see_all else Program.objects.filter(is_active=True)


# ─── Documents ────────────────────────────────────────────────────────────────

class DocumentListView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


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
