from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Event, PromotionBanner, CompetitionAlertSubscription, Competition, NewsPost, NewsCategory
from .serializers import (
    EventSerializer, EventWriteSerializer,
    PromotionBannerSerializer,
    CompetitionAlertSubscriptionSerializer,
    CompetitionSerializer, CompetitionWriteSerializer,
    NewsPostSerializer, NewsPostWriteSerializer,
    NewsCategorySerializer,
)
from users.permissions import IsAdminOrModeratorOrReadOnly, IsCandidate

class EventActiveListView(generics.ListAPIView):
    """Endpoint public pour lister les événements à venir dans l'agenda"""
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # On ne renvoie que les événements qui ne sont pas encore terminés
        return Event.objects.filter(is_public=True, end_date__gte=timezone.now())


class EventDetailView(generics.RetrieveAPIView):
    """Endpoint public pour voir les détails d'un événement via son slug"""
    queryset = Event.objects.filter(is_public=True)
    serializer_class = EventSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


class ActiveBannerListView(generics.ListAPIView):
    """Endpoint public pour récupérer les bannières publicitaires actives en ce moment sur la page d'accueil"""
    serializer_class = PromotionBannerSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return PromotionBanner.objects.filter(
            is_active=True,
            start_display__lte=now,
            end_display__gte=now
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_banner_click(request, banner_id):
    """Endpoint appelé lorsque l'utilisateur clique sur une bannière (KPI de la DCM)"""
    banner = get_object_or_404(PromotionBanner, id=banner_id)
    banner.click_count += 1
    banner.save()
    return Response({'status': 'click tracked', 'current_clicks': banner.click_count}, status=status.HTTP_200_OK)


class CompetitionAlertSubscribeView(generics.GenericAPIView):
    """
    POST  — S'abonner / se réabonner aux alertes concours.
             • Candidat authentifié : réactive receive_competition_notifications.
             • Autre / anonyme      : crée une entrée CompetitionAlertSubscription par email.
    DELETE — Se désabonner :
             • Candidat authentifié : désactive receive_competition_notifications.
             • Autre / anonyme      : supprime l'entrée CompetitionAlertSubscription par email.
    """
    serializer_class = CompetitionAlertSubscriptionSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = request.user
        if user.is_authenticated and user.role == 'candidate':
            if user.receive_competition_notifications:
                return Response(
                    {'detail': 'Vous êtes déjà abonné(e) aux alertes concours.'},
                    status=status.HTTP_200_OK,
                )
            user.receive_competition_notifications = True
            user.save(update_fields=['receive_competition_notifications'])
            return Response(
                {'detail': 'Vous êtes à nouveau abonné(e) aux alertes concours.'},
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        user = request.user
        if user.is_authenticated and user.role == 'candidate':
            user.receive_competition_notifications = False
            user.save(update_fields=['receive_competition_notifications'])
            return Response(status=status.HTTP_204_NO_CONTENT)

        email = request.data.get('email')
        if not email:
            return Response({'error': 'email requis'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = CompetitionAlertSubscription.objects.filter(email=email).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Abonnement introuvable'}, status=status.HTTP_404_NOT_FOUND)


class CompetitionAlertStatusView(generics.GenericAPIView):
    """
    GET — Retourne le statut d'abonnement aux alertes concours pour l'utilisateur connecté.
          • Candidat : indique si receive_competition_notifications est actif.
          • Autre rôle : indique si l'email est dans CompetitionAlertSubscription.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'candidate':
            return Response({'subscribed': user.receive_competition_notifications})
        subscribed = CompetitionAlertSubscription.objects.filter(email=user.email).exists()
        return Response({'subscribed': subscribed})


class NewsPostListView(generics.ListAPIView):
    """Endpoint public pour lister les actualités et communiqués de presse publiés"""
    serializer_class = NewsPostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = NewsPost.objects.filter(is_published=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__code=category)
        return queryset


class NewsPostDetailView(generics.RetrieveAPIView):
    """Endpoint public pour lire une actualité complète via son slug"""
    queryset = NewsPost.objects.filter(is_published=True)
    serializer_class = NewsPostSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


class NewsCategoryListView(generics.ListAPIView):
    """Endpoint public — catégories d'actualités disponibles pour filtrer les actualités."""
    queryset = NewsCategory.objects.filter(is_active=True)
    serializer_class = NewsCategorySerializer
    permission_classes = [permissions.AllowAny]


def _active_competitions_qs():
    """Retourne les concours ouverts et non expirés (date du concours non dépassée)."""
    today = timezone.now().date()
    return Competition.objects.filter(
        is_active=True
    ).filter(
        Q(competition_date__isnull=True) | Q(competition_date__gte=today)
    )


class CompetitionPublicListView(generics.ListAPIView):
    """Endpoint public — liste les concours ouverts et non expirés."""
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return _active_competitions_qs()


class CandidateCompetitionsView(generics.ListAPIView):
    """Espace candidat — liste les concours actifs et non expirés. Réservé aux utilisateurs avec role=candidate."""
    serializer_class = CompetitionSerializer
    permission_classes = [IsCandidate]

    def get_queryset(self):
        return _active_competitions_qs()


class CompetitionPublicDetailView(generics.RetrieveAPIView):
    """Endpoint public — détail d'un concours via son slug (masqué si expiré)."""
    serializer_class = CompetitionSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return _active_competitions_qs()


# ─── Admin manage views ───────────────────────────────────────────────────────

class EventAdminListCreateView(generics.ListCreateAPIView):
    """Admin: liste tous les événements (y compris non-publics) et permet la création."""
    queryset = Event.objects.all()
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventWriteSerializer
        return EventSerializer


class EventAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: modifier ou supprimer un événement."""
    queryset = Event.objects.all()
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return EventWriteSerializer
        return EventSerializer


class PromotionBannerAdminListCreateView(generics.ListCreateAPIView):
    """Admin: liste toutes les bannières (y compris inactives) et permet la création."""
    queryset = PromotionBanner.objects.all()
    serializer_class = PromotionBannerSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class PromotionBannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: modifier ou supprimer une bannière."""
    queryset = PromotionBanner.objects.all()
    serializer_class = PromotionBannerSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class CompetitionAdminListCreateView(generics.ListCreateAPIView):
    """Admin: liste tous les concours (actifs et inactifs) et permet la création."""
    queryset = Competition.objects.all()
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CompetitionWriteSerializer
        return CompetitionSerializer


class CompetitionAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: modifier ou supprimer un concours. Déclenche les notifications quand is_active passe à True."""
    queryset = Competition.objects.all()
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return CompetitionWriteSerializer
        return CompetitionSerializer

    def perform_update(self, serializer):
        was_active = serializer.instance.is_active
        competition = serializer.save()
        if not was_active and competition.is_active:
            from users.utils import send_competition_launch_notifications
            send_competition_launch_notifications(competition)


class NewsPostAdminListCreateView(generics.ListCreateAPIView):
    """Admin: liste tous les articles (publiés et non publiés) et permet la création."""
    queryset = NewsPost.objects.all()
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewsPostWriteSerializer
        return NewsPostSerializer


class NewsPostAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: modifier ou supprimer un article."""
    queryset = NewsPost.objects.all()
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return NewsPostWriteSerializer
        return NewsPostSerializer


class NewsCategoryAdminListCreateView(generics.ListCreateAPIView):
    """Admin: liste toutes les catégories et permet la création."""
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class NewsCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: modifier ou supprimer une catégorie d'actualités."""
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'code'