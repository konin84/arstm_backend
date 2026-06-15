# apps/library/serializers.py
from rest_framework import serializers
from .models import ResearchPaper, SectorWatch, Category
from academic.serializers import DomainSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ResearchPaperSerializer(serializers.ModelSerializer):
    domain_detail = DomainSerializer(source='domain', read_only=True)

    class Meta:
        model = ResearchPaper
        fields = [
            'id', 'title', 'slug', 'domain', 'domain_detail', 'authors', 
            'abstract', 'pdf_file', 'views_count', 'download_count', 'created_at'
        ]


class SectorWatchSerializer(serializers.ModelSerializer):
    # Permet d'avoir l'objet complet de la catégorie (id, name, slug) au lieu du simple ID numérique
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = SectorWatch
        fields = ['id', 'title', 'slug', 'category', 'category_detail', 'content', 'featured_image', 'created_at']