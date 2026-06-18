# apps/interactions/views.py
from rest_framework import generics, permissions
from .models import ContactRequest, AdmissionRequest, InternshipRequest, JobOffer, Lead
from .serializers import (
    ContactRequestSerializer, AdmissionRequestSerializer,
    InternshipRequestSerializer, JobOfferSerializer, JobOfferWriteSerializer,
    LeadSerializer,
)
from users.permissions import IsAdminOrModerator, IsAdminOrModeratorOrReadOnly, PRIVILEGED_ROLES


# ─── Soumissions publiques ────────────────────────────────────────────────────

class ContactCreateView(generics.CreateAPIView):
    """Endpoint public pour soumettre le formulaire de contact général"""
    queryset = ContactRequest.objects.all()
    serializer_class = ContactRequestSerializer
    permission_classes = [permissions.AllowAny]


class AdmissionCreateView(generics.CreateAPIView):
    """Endpoint public pour soumettre une demande de pré-inscription/concours"""
    queryset = AdmissionRequest.objects.all()
    serializer_class = AdmissionRequestSerializer
    permission_classes = [permissions.AllowAny]


class InternshipCreateView(generics.CreateAPIView):
    """Endpoint public pour soumettre des candidatures de stage ou d'emploi (avec dépôt de CV)"""
    queryset = InternshipRequest.objects.all()
    serializer_class = InternshipRequestSerializer
    permission_classes = [permissions.AllowAny]


# ─── Offres d'emploi / stage ──────────────────────────────────────────────────

class JobOfferListView(generics.ListCreateAPIView):
    """Lecture publique (offres actives) ; création réservée aux admins et modérateurs."""
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobOfferWriteSerializer
        return JobOfferSerializer

    def get_queryset(self):
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_staff or getattr(user, 'role', None) in PRIVILEGED_ROLES
        )
        queryset = JobOffer.objects.all() if is_privileged else JobOffer.objects.filter(is_active=True)
        offer_type = self.request.query_params.get('type')
        if offer_type:
            queryset = queryset.filter(offer_type=offer_type)
        return queryset


class JobOfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Lecture publique (offres actives) ; modification et suppression réservées aux admins et modérateurs."""
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return JobOfferWriteSerializer
        return JobOfferSerializer

    def get_queryset(self):
        user = self.request.user
        is_privileged = user.is_authenticated and (
            user.is_staff or getattr(user, 'role', None) in PRIVILEGED_ROLES
        )
        return JobOffer.objects.all() if is_privileged else JobOffer.objects.filter(is_active=True)


# ─── Gestion admin des leads et demandes ─────────────────────────────────────

class LeadListView(generics.ListAPIView):
    """Admin/Modérateur : liste de tous les leads capturés."""
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAdminOrModerator]


class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin/Modérateur : consulter, mettre à jour le statut ou supprimer un lead."""
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAdminOrModerator]


class ContactRequestAdminListView(generics.ListAPIView):
    """Admin/Modérateur : liste de toutes les demandes de contact."""
    queryset = ContactRequest.objects.select_related('lead').all()
    serializer_class = ContactRequestSerializer
    permission_classes = [IsAdminOrModerator]


class AdmissionRequestAdminListView(generics.ListAPIView):
    """Admin/Modérateur : liste de toutes les demandes d'admission."""
    queryset = AdmissionRequest.objects.select_related('lead').all()
    serializer_class = AdmissionRequestSerializer
    permission_classes = [IsAdminOrModerator]


class InternshipRequestAdminListView(generics.ListAPIView):
    """Admin/Modérateur : liste de toutes les candidatures de stage/emploi."""
    queryset = InternshipRequest.objects.select_related('lead').all()
    serializer_class = InternshipRequestSerializer
    permission_classes = [IsAdminOrModerator]
