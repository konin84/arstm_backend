# apps/library/views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ResearchPaper, SectorWatch, Category
from .serializers import ResearchPaperSerializer, SectorWatchSerializer, CategorySerializer
from users.permissions import IsAdminOrModeratorOrReadOnly


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'


class ResearchPaperListView(generics.ListCreateAPIView):
    queryset = ResearchPaper.objects.all().order_by('-created_at')
    serializer_class = ResearchPaperSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class ResearchPaperDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResearchPaper.objects.all()
    serializer_class = ResearchPaperSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return Response(self.get_serializer(instance).data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_paper_download(request, paper_id):
    paper = get_object_or_404(ResearchPaper, id=paper_id)
    paper.download_count += 1
    paper.save(update_fields=['download_count'])
    return Response({'status': 'download tracked', 'download_count': paper.download_count}, status=status.HTTP_200_OK)


class SectorWatchListView(generics.ListCreateAPIView):
    queryset = SectorWatch.objects.all().order_by('-created_at')
    serializer_class = SectorWatchSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class SectorWatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SectorWatch.objects.all()
    serializer_class = SectorWatchSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'
