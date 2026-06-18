# apps/events/serializers.py
from rest_framework import serializers
from .models import Event, PromotionBanner, CompetitionAlertSubscription, NewsPost, NewsCategory


class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ['id', 'code', 'label', 'is_active', 'order']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'slug', 'description', 'start_date', 'end_date', 'location', 'image', 'is_public']


class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'location', 'image', 'is_public']


class PromotionBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionBanner
        fields = ['id', 'title', 'image', 'target_url', 'click_count', 'start_display', 'end_display', 'is_active']
        read_only_fields = ['click_count']


class CompetitionAlertSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionAlertSubscription
        fields = ['id', 'email', 'full_name', 'subscribed_at']


class NewsPostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='code', read_only=True)
    category_display = serializers.CharField(source='category.label', read_only=True)

    class Meta:
        model = NewsPost
        fields = ['id', 'title', 'slug', 'category', 'category_display', 'content', 'featured_image', 'is_published', 'published_at']


class NewsPostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = ['id', 'title', 'category', 'content', 'featured_image', 'is_published', 'published_at']