# apps/analytics/serializers.py
from rest_framework import serializers
from .models import ContentTraffic

class ContentTrafficSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentTraffic
        fields = ['id', 'content_type', 'object_id', 'action', 'visitor_country', 'timestamp']