# apps/interactions/views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import ContactRequest, AdmissionRequest, InternshipRequest, JobOffer, Lead, NewsletterSubscription
from .serializers import (
    ContactRequestSerializer, AdmissionRequestSerializer,
    InternshipRequestSerializer, JobOfferSerializer, JobOfferWriteSerializer,
    LeadSerializer, NewsletterBroadcastSerializer, NewsletterSubscriptionSerializer, NewsletterUnsubscribeSerializer,
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


# ─── Espace utilisateur ──────────────────────────────────────────────────────

class MyAdmissionsView(generics.ListAPIView):
    """Endpoint authentifié — liste les demandes d'admission liées à l'email du compte connecté."""
    serializer_class = AdmissionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AdmissionRequest.objects.filter(
            lead__email=self.request.user.email
        ).select_related('lead')


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


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def newsletter_token_unsubscribe(request):
    """Lien de désabonnement depuis l'email — GET /newsletter/unsubscribe?token=..."""
    from users.utils import verify_unsubscribe_token, send_newsletter_unsubscribe_email
    token = request.query_params.get('token')
    if not token:
        return Response({'detail': 'Token manquant.'}, status=status.HTTP_400_BAD_REQUEST)

    email = verify_unsubscribe_token(token)
    if not email:
        return Response({'detail': 'Lien invalide ou expiré.'}, status=status.HTTP_400_BAD_REQUEST)

    subscription = NewsletterSubscription.objects.filter(lead__email=email).first()
    if subscription and subscription.is_active:
        subscription.is_active = False
        subscription.save()
        send_newsletter_unsubscribe_email(email)

    return Response({'detail': 'Vous avez été désabonné(e) avec succès.'}, status=status.HTTP_200_OK)


class NewsletterSubscribeView(generics.CreateAPIView):
    """Endpoint public pour s'abonner à la newsletter de l'ARSTM (ex: depuis le footer)"""
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [permissions.AllowAny]



class NewsletterUnsubscribeView(generics.GenericAPIView):
    """Endpoint public pour se désabonner de la newsletter de l'ARSTM"""
    serializer_class = NewsletterUnsubscribeSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Vous avez été désabonné(e) avec succès."},
            status=status.HTTP_200_OK
        )
    
class NewsletterBroadcastView(generics.GenericAPIView):
    """Admin/Modérateur : envoie un message à tous les abonnés actifs de la newsletter."""
    serializer_class = NewsletterBroadcastSerializer
    permission_classes = [IsAdminOrModerator]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        count = send_newsletter_broadcast(
            subject=serializer.validated_data['subject'],
            html_content=serializer.validated_data['message'],
        )
        return Response(
            {"detail": f"Diffusion lancée pour {count} abonné(e)s actifs."},
            status=status.HTTP_202_ACCEPTED
        )