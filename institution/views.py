from rest_framework import generics, permissions
from .models import School, Infrastructure, Partner, Testimonial
from .serializers import SchoolSerializer, InfrastructureSerializer, PartnerSerializer, TestimonialSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Lecture publique, écriture réservée aux admins (is_staff)."""
    def has_permission(self, request, _view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# ─── Schools ──────────────────────────────────────────────────────────────────

class SchoolListView(generics.ListCreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAdminOrReadOnly]


class SchoolDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# ─── Infrastructures ──────────────────────────────────────────────────────────

class InfrastructureListView(generics.ListCreateAPIView):
    queryset = Infrastructure.objects.all()
    serializer_class = InfrastructureSerializer
    permission_classes = [IsAdminOrReadOnly]


class InfrastructureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Infrastructure.objects.all()
    serializer_class = InfrastructureSerializer
    permission_classes = [IsAdminOrReadOnly]


# ─── Partners ─────────────────────────────────────────────────────────────────

class PartnerListView(generics.ListCreateAPIView):
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Partner.objects.all()
        partner_type = self.request.query_params.get('type')
        if partner_type:
            queryset = queryset.filter(partner_type=partner_type)
        return queryset


class PartnerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]


# ─── Testimonials ─────────────────────────────────────────────────────────────

class TestimonialListView(generics.ListCreateAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Testimonial.objects.all()
        if self.request.query_params.get('featured') == 'true':
            queryset = queryset.filter(is_featured=True)
        return queryset


class TestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]
