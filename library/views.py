# apps/library/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ResearchPaper, SectorWatch
from .serializers import ResearchPaperSerializer, SectorWatchSerializer

class ResearchPaperListView(generics.ListAPIView):
    """Endpoint public pour lister les publications scientifiques du CREMPOL"""
    queryset = ResearchPaper.objects.all().order_by('-created_at')
    serializer_class = ResearchPaperSerializer


class ResearchPaperDetailView(generics.RetrieveAPIView):
    """Endpoint public pour consulter une publication et incrémenter le compteur de vues (KPI)"""
    queryset = ResearchPaper.objects.all()
    serializer_class = ResearchPaperSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrémentation automatique du compteur de consultations
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
def track_paper_download(request, paper_id):
    """Endpoint pour enregistrer le téléchargement effectif d'un fichier PDF de recherche"""
    paper = get_object_or_404(ResearchPaper, id=paper_id)
    paper.download_count += 1
    paper.save(update_fields=['download_count'])
    return Response({'status': 'download tracked', 'download_count': paper.download_count}, status=status.HTTP_200_OK)


class SectorWatchListView(generics.ListAPIView):
    """Endpoint public pour lister les articles de veille sectorielle"""
    queryset = SectorWatch.objects.all().order_by('-created_at')
    serializer_class = SectorWatchSerializer


class SectorWatchDetailView(generics.RetrieveAPIView):
    """Endpoint public pour lire un article de veille complet via son slug"""
    queryset = SectorWatch.objects.all()
    serializer_class = SectorWatchSerializer
    lookup_field = 'slug'