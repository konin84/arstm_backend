from rest_framework import serializers
from .models import School, Infrastructure, Partner, Testimonial

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'slug', 'description', 'description_fr', 'description_en',
                  'presentation_video_url', 'featured_image']
        read_only_fields = ['slug']


class InfrastructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Infrastructure
        fields = ['id', 'title', 'title_fr', 'title_en', 'description', 'description_fr', 'description_en', 'image']


class PartnerSerializer(serializers.ModelSerializer):
    partner_type_display = serializers.CharField(source='get_partner_type_display', read_only=True)

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