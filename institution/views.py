from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from .models import School, Infrastructure, Partner, PartnerType, Testimonial, DirectorMessage
from .serializers import (
    SchoolSerializer, InfrastructureSerializer, PartnerSerializer, PartnerTypeSerializer, TestimonialSerializer,
    DirectorMessageSerializer,
)
from users.permissions import IsAdminOrModeratorOrReadOnly


# ─── Schools ──────────────────────────────────────────────────────────────────

class SchoolListView(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class SchoolDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
    lookup_field = 'slug'


# ─── Director message ────────────────────────────────────────────────────────

class DirectorMessageListView(generics.ListCreateAPIView):
    queryset = DirectorMessage.objects.all()
    serializer_class = DirectorMessageSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class DirectorMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DirectorMessage.objects.all()
    serializer_class = DirectorMessageSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class DirectorMessageActiveView(generics.RetrieveAPIView):
    """Renvoie le mot du Directeur actuellement actif, pour la page publique."""
    serializer_class = DirectorMessageSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        instance = DirectorMessage.objects.filter(is_active=True).first()
        if not instance:
            raise NotFound("Aucun mot du Directeur actif.")
        return instance


# ─── Infrastructures ──────────────────────────────────────────────────────────

class InfrastructureListView(generics.ListCreateAPIView):
    queryset = Infrastructure.objects.all()
    serializer_class = InfrastructureSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class InfrastructureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Infrastructure.objects.all()
    serializer_class = InfrastructureSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


# ─── Partner types (liste dynamique) ───────────────────────────────────────────

class PartnerTypeListView(generics.ListAPIView):
    """Endpoint public — types de partenaires disponibles pour filtrer/créer un partenaire."""
    queryset = PartnerType.objects.filter(is_active=True)
    serializer_class = PartnerTypeSerializer
    permission_classes = [permissions.AllowAny]


# ─── Partners ─────────────────────────────────────────────────────────────────

class PartnerListView(generics.ListCreateAPIView):
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        queryset = Partner.objects.all()
        partner_type = self.request.query_params.get('type')
        if partner_type:
            queryset = queryset.filter(partner_type__code=partner_type)
        return queryset


class PartnerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


# ─── Testimonials ─────────────────────────────────────────────────────────────

class TestimonialListView(generics.ListCreateAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        queryset = Testimonial.objects.all()
        if self.request.query_params.get('featured') == 'true':
            queryset = queryset.filter(is_featured=True)
        return queryset


class TestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]
