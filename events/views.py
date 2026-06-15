from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Event, PromotionBanner, CompetitionAlertSubscription, NewsPost
from .serializers import EventSerializer, PromotionBannerSerializer, CompetitionAlertSubscriptionSerializer, NewsPostSerializer

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


class CompetitionAlertSubscribeView(generics.CreateAPIView):
    """Endpoint public permettant aux candidats de s'abonner aux alertes de concours"""
    queryset = CompetitionAlertSubscription.objects.all()
    serializer_class = CompetitionAlertSubscriptionSerializer
    permission_classes = [permissions.AllowAny]


class NewsPostListView(generics.ListAPIView):
    """Endpoint public pour lister les actualités et communiqués de presse publiés"""
    serializer_class = NewsPostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = NewsPost.objects.filter(is_published=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class NewsPostDetailView(generics.RetrieveAPIView):
    """Endpoint public pour lire une actualité complète via son slug"""
    queryset = NewsPost.objects.filter(is_published=True)
    serializer_class = NewsPostSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]