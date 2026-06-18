# apps/analytics/views.py
from rest_framework import views, generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count
from .models import ContentTraffic
from .serializers import ContentTrafficSerializer
from interactions.models import Lead
from users.permissions import IsAdmin


class TrackActionView(generics.CreateAPIView):
    """Endpoint public permettant au frontend d'envoyer une interaction (clic, vue)"""
    queryset = ContentTraffic.objects.all()
    serializer_class = ContentTrafficSerializer
    permission_classes = [permissions.AllowAny]


class DCMDashboardStatsView(views.APIView):
    """
    Endpoint hautement stratégique compilant les statistiques globales pour la Direction.
    Affiche le statut de l'objectif des 100 leads et la répartition géographique.
    """
    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):

        now = timezone.now()

        # 1. État de l'objectif Leads Mensuels (KPI : 100 / mois)
        leads_this_month = Lead.objects.filter(created_at__year=now.year, created_at__month=now.month).count()
        lead_target = 100
        kpi_progress = round((leads_this_month / lead_target) * 100, 2)

        # 2. Top des pays d'origine des visiteurs (Répartition régionale)
        geo_distribution = ContentTraffic.objects.values('visitor_country')\
            .annotate(total_actions=Count('id'))\
            .order_by('-total_actions')[:5]

        # 3. Volume total des actions du mois
        total_clicks = ContentTraffic.objects.filter(action='click', timestamp__month=now.month).count()
        total_downloads = ContentTraffic.objects.filter(action='download', timestamp__month=now.month).count()

        return Response({
            "reporting_period": now.strftime("%B %Y"),
            "kpi_leads": {
                "current_month_total": leads_this_month,
                "target": lead_target,
                "percentage_reached": min(kpi_progress, 100.0)
            },
            "traffic_metrics": {
                "total_clicks_this_month": total_clicks,
                "total_downloads_this_month": total_downloads
            },
            "regional_impact_top_countries": geo_distribution
        }, status=status.HTTP_200_OK)