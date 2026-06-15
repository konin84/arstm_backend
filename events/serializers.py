# apps/events/serializers.py
from rest_framework import serializers
from .models import Event, PromotionBanner, CompetitionAlertSubscription, NewsPost

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        # On ne passe que les champs natifs. DRF renverra la traduction active.
        fields = ['id', 'title', 'slug', 'description', 'start_date', 'end_date', 'location', 'image']


class PromotionBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionBanner
        fields = ['id', 'title', 'image', 'target_url', 'click_count']


class CompetitionAlertSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionAlertSubscription
        fields = ['id', 'email', 'full_name', 'subscribed_at']


class NewsPostSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = NewsPost
        fields = ['id', 'title', 'slug', 'category', 'category_display', 'content', 'featured_image', 'published_at']