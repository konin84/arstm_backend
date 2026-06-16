from rest_framework import serializers
from .models import Domain, Program, ProgramType, Regime, Document
from institution.serializers import SchoolSerializer


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'program', 'title', 'file', 'download_count']
        read_only_fields = ['download_count']


class ProgramTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramType
        fields = ['code', 'label']


class RegimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regime
        fields = ['code', 'label']


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class ProgramListSerializer(serializers.ModelSerializer):
    """Lecture seule — liste légère pour la page d'exploration."""
    domain_name = serializers.CharField(source='domain.name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    program_type = serializers.SlugRelatedField(slug_field='code', read_only=True)
    regime = serializers.SlugRelatedField(slug_field='code', read_only=True)

    class Meta:
        model = Program
        fields = [
            'id', 'title', 'slug', 'program_type',
            'regime', 'duration', 'domain_name', 'school_name',
        ]


class ProgramDetailSerializer(serializers.ModelSerializer):
    """Lecture seule — fiche complète avec relations imbriquées."""
    domain = DomainSerializer(read_only=True)
    school = SchoolSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    program_type = serializers.SlugRelatedField(slug_field='code', read_only=True)
    regime = serializers.SlugRelatedField(slug_field='code', read_only=True)

    class Meta:
        model = Program
        fields = [
            'id', 'title', 'slug', 'program_type', 'regime', 'duration',
            'description', 'career_opportunities',
            'domain', 'school', 'documents', 'is_active',
            'meta_title', 'meta_description',
        ]


class ProgramWriteSerializer(serializers.ModelSerializer):
    """Création et mise à jour — utilise les IDs FK pour domain et school."""
    program_type = serializers.SlugRelatedField(slug_field='code', queryset=ProgramType.objects.filter(is_active=True))
    regime = serializers.SlugRelatedField(slug_field='code', queryset=Regime.objects.filter(is_active=True), required=False, allow_null=True)

    class Meta:
        model = Program
        fields = [
            'id', 'domain', 'school', 'title', 'slug',
            'program_type', 'regime', 'duration',
            'description', 'career_opportunities',
            'is_active', 'meta_title', 'meta_description',
        ]
        read_only_fields = ['slug']