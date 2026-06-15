# apps/interactions/views.py
from rest_framework import generics, permissions
from .models import ContactRequest, AdmissionRequest, InternshipRequest, JobOffer
from .serializers import ContactRequestSerializer, AdmissionRequestSerializer, InternshipRequestSerializer, JobOfferSerializer

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


class JobOfferListView(generics.ListAPIView):
    """Endpoint public pour lister les offres de stage et d'emploi actives"""
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = JobOffer.objects.filter(is_active=True)
        offer_type = self.request.query_params.get('type')
        if offer_type:
            queryset = queryset.filter(offer_type=offer_type)
        return queryset


class JobOfferDetailView(generics.RetrieveAPIView):
    """Endpoint public pour consulter une offre via son slug"""
    queryset = JobOffer.objects.filter(is_active=True)
    serializer_class = JobOfferSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]