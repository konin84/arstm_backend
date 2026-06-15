from rest_framework import serializers
from .models import Domain, Program, Document
from institution.serializers import SchoolSerializer


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'program', 'title', 'file', 'download_count']
        read_only_fields = ['download_count']


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'name', 'name_fr', 'name_en', 'slug']
        read_only_fields = ['slug']


class ProgramListSerializer(serializers.ModelSerializer):
    """Lecture seule — liste légère pour la page d'exploration."""
    domain_name = serializers.CharField(source='domain.name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = Program
        fields = [
            'id', 'title', 'title_fr', 'title_en', 'slug', 'program_type',
            'regime', 'duration', 'domain_name', 'school_name',
        ]


class ProgramDetailSerializer(serializers.ModelSerializer):
    """Lecture seule — fiche complète avec relations imbriquées."""
    domain = DomainSerializer(read_only=True)
    school = SchoolSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = [
            'id', 'title', 'title_fr', 'title_en', 'slug', 'program_type', 'regime', 'duration',
            'description', 'description_fr', 'description_en',
            'career_opportunities', 'career_opportunities_fr', 'career_opportunities_en',
            'domain', 'school', 'documents', 'is_active',
            'meta_title', 'meta_description',
        ]


class ProgramWriteSerializer(serializers.ModelSerializer):
    """Création et mise à jour — utilise les IDs FK pour domain et school."""
    class Meta:
        model = Program
        fields = [
            'id', 'domain', 'school', 'title', 'title_fr', 'title_en', 'slug',
            'program_type', 'regime', 'duration',
            'description', 'description_fr', 'description_en',
            'career_opportunities', 'career_opportunities_fr', 'career_opportunities_en',
            'is_active', 'meta_title', 'meta_description',
        ]
        read_only_fields = ['slug']