# apps/interactions/serializers.py
from rest_framework import serializers
from django.db import transaction

from users.utils import send_newsletter_confirmation_email, send_newsletter_unsubscribe_email
from .models import Lead, ContactRequest, AdmissionRequest, InternshipRequest, JobOffer, NewsletterSubscription

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'source', 'status', 'created_at']


class ContactRequestSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    phone = serializers.CharField(write_only=True)
    
    lead = LeadSerializer(read_only=True)

    class Meta:
        model = ContactRequest
        fields = ['id', 'lead', 'first_name', 'last_name', 'email', 'phone', 'subject', 'message']

    @transaction.atomic
    def create(self, validated_data):
        lead_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'phone': validated_data.pop('phone'),
            'source': 'contact'
        }
        lead = Lead.objects.create(**lead_data)
        return ContactRequest.objects.create(lead=lead, **validated_data)


class AdmissionRequestSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    phone = serializers.CharField(write_only=True)
    
    lead = LeadSerializer(read_only=True)

    class Meta:
        model = AdmissionRequest
        fields = ['id', 'lead', 'first_name', 'last_name', 'email', 'phone', 'program', 'academic_level', 'birth_date']

    @transaction.atomic
    def create(self, validated_data):
        lead_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'phone': validated_data.pop('phone'),
            'source': 'admission'
        }
        lead = Lead.objects.create(**lead_data)
        return AdmissionRequest.objects.create(lead=lead, **validated_data)


class InternshipRequestSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    phone = serializers.CharField(write_only=True)
    
    lead = LeadSerializer(read_only=True)

    class Meta:
        model = InternshipRequest
        fields = ['id', 'lead', 'first_name', 'last_name', 'email', 'phone', 'request_type', 'cv_file', 'cover_letter']

    @transaction.atomic
    def create(self, validated_data):
        lead_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'phone': validated_data.pop('phone'),
            'source': 'internship'
        }
        lead = Lead.objects.create(**lead_data)
        return InternshipRequest.objects.create(lead=lead, **validated_data)


class JobOfferSerializer(serializers.ModelSerializer):
    offer_type_display = serializers.CharField(source='get_offer_type_display', read_only=True)

    class Meta:
        model = JobOffer
        fields = ['id', 'title', 'slug', 'offer_type', 'offer_type_display', 'organization', 'location', 'description', 'requirements', 'deadline', 'is_active', 'created_at']


class JobOfferWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = ['id', 'title', 'offer_type', 'organization', 'location', 'description', 'requirements', 'deadline', 'is_active']


# ───────────────────────────────────────────────────────────────────────────────
# Serializers pour la gestion de la newsletter (abonnement/désabonnement)
class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    lead = LeadSerializer(read_only=True)

    class Meta:
        model = NewsletterSubscription
        fields = ['id', 'lead', 'email', 'is_active']
        read_only_fields = ['is_active']

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop('email')

        existing_sub = NewsletterSubscription.objects.filter(lead__email=email).first()
        if existing_sub:
            if not existing_sub.is_active:
                existing_sub.is_active = True
                existing_sub.save()
            send_newsletter_confirmation_email(email)
            return existing_sub

        lead = Lead.objects.create(
            email=email,
            source='newsletter'
        )
        subscription = NewsletterSubscription.objects.create(lead=lead, **validated_data)
        send_newsletter_confirmation_email(email)
        return subscription


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self, **kwargs):
        email = self.validated_data['email']
        subscription = NewsletterSubscription.objects.filter(lead__email=email).first()

        if subscription and subscription.is_active:
            subscription.is_active = False
            subscription.save()
            send_newsletter_unsubscribe_email(email)

        return subscription