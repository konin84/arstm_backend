from rest_framework import serializers
from .models import School, Infrastructure, Partner, PartnerType, Testimonial, DirectorMessage

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            'id', 'name', 'slug', 'description',
            'director_name', 'address', 'city', 'country', 'phone', 'email',
            'founded_year', 'accreditation',
            'website_url', 'presentation_video_url', 'featured_image',
        ]
        read_only_fields = ['slug']


class DirectorMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectorMessage
        fields = ['id', 'full_name', 'title', 'photo', 'message', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class InfrastructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Infrastructure
        fields = ['id', 'title', 'description', 'image']


class PartnerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerType
        fields = ['code', 'label']


class PartnerSerializer(serializers.ModelSerializer):
    partner_type = serializers.SlugRelatedField(slug_field='code', queryset=PartnerType.objects.filter(is_active=True))
    partner_type_display = serializers.CharField(source='partner_type.label', read_only=True)

    class Meta:
        model = Partner
        fields = ['id', 'name', 'partner_type', 'partner_type_display', 'logo', 'website_url']


class TestimonialSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = Testimonial
        fields = ['id', 'full_name', 'current_position', 'school', 'school_name',
                  'content', 'photo', 'is_featured', 'created_at']
        read_only_fields = ['school_name', 'created_at']