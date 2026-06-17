from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    StudentProfile, ProfessionalProfile,
    ResearcherProfile, InstitutionalProfile, StaffProfile,
    Sector, OrganizationType,
)

User = get_user_model()


# ─── Listes de valeurs dynamiques ───────────────────────────────────────────

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['code', 'label']


class OrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = ['code', 'label']


# ─── Profil serializers ───────────────────────────────────────────────────────

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['school', 'matricule', 'current_year', 'birth_date', 'nationality']


class ProfessionalProfileSerializer(serializers.ModelSerializer):
    sector = serializers.SlugRelatedField(
        slug_field='code', queryset=Sector.objects.filter(is_active=True), required=False, allow_null=True,
    )

    class Meta:
        model = ProfessionalProfile
        fields = ['company_name', 'job_title', 'sector', 'country', 'company_website']


class ResearcherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearcherProfile
        fields = ['academic_title', 'institution', 'specialization', 'country', 'research_profile_url']


class InstitutionalProfileSerializer(serializers.ModelSerializer):
    organization_type = serializers.SlugRelatedField(
        slug_field='code', queryset=OrganizationType.objects.filter(is_active=True), required=False, allow_null=True,
    )

    class Meta:
        model = InstitutionalProfile
        fields = ['organization_name', 'position', 'organization_type', 'country']


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = ['department', 'employee_id']


# ─── User serializers ─────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """Profil complet de l'utilisateur connecté — inclut le bon profil selon le rôle."""
    student_profile = StudentProfileSerializer(read_only=True)
    professional_profile = ProfessionalProfileSerializer(read_only=True)
    researcher_profile = ResearcherProfileSerializer(read_only=True)
    institutional_profile = InstitutionalProfileSerializer(read_only=True)
    staff_profile = StaffProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'phone', 'avatar',
            'must_change_password',
            'student_profile', 'professional_profile',
            'researcher_profile', 'institutional_profile', 'staff_profile',
        ]
        read_only_fields = ['id', 'role', 'must_change_password']


# Maps each role to its (profile_field, profile_model, profile_serializer)
ROLE_PROFILE_MAP = {
    'student':      ('student_profile',      StudentProfile,      StudentProfileSerializer),
    'professional': ('professional_profile', ProfessionalProfile, ProfessionalProfileSerializer),
    'recruiter':    ('professional_profile', ProfessionalProfile, ProfessionalProfileSerializer),
    'researcher':   ('researcher_profile',   ResearcherProfile,   ResearcherProfileSerializer),
    'donor':        ('institutional_profile',InstitutionalProfile,InstitutionalProfileSerializer),
    'moderator':    ('staff_profile',        StaffProfile,        StaffProfileSerializer),
    'admin':        ('staff_profile',        StaffProfile,        StaffProfileSerializer),
}

# Roles that only an admin can assign — blocked from public registration and moderator creation
RESTRICTED_ROLES = ('admin', 'moderator')


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """Création de compte par un administrateur. Le mot de passe est saisi manuellement."""
    profile = serializers.DictField(child=serializers.CharField(allow_blank=True), required=False)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'role', 'password', 'profile']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Un utilisateur avec ce numéro existe déjà.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password')
        role = validated_data.get('role', 'student')

        user = User.objects.create_user(password=password, **validated_data)

        if role in ROLE_PROFILE_MAP:
            _, ProfileModel, ProfileSerializer = ROLE_PROFILE_MAP[role]
            profile_serializer = ProfileSerializer(data=profile_data)
            profile_serializer.is_valid(raise_exception=True)
            ProfileModel.objects.create(user=user, **profile_serializer.validated_data)

        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Auto-inscription publique.
    Les étudiants n'ont pas de mot de passe à ce stade — il leur sera défini lors
    de l'activation du compte par un administrateur.
    Les autres rôles saisissent leur mot de passe directement.
    """
    profile = serializers.DictField(child=serializers.CharField(allow_blank=True), required=False)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'phone', 'password', 'profile']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Un utilisateur avec ce numéro existe déjà.")
        return value

    def validate_role(self, value):
        if value in RESTRICTED_ROLES:
            raise serializers.ValidationError("Ce rôle ne peut pas être attribué lors de l'inscription publique.")
        return value

    def validate(self, attrs):
        role = attrs.get('role', 'student')
        if role != 'student' and not attrs.get('password'):
            raise serializers.ValidationError({"password": "Ce champ est obligatoire pour ce rôle."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)
        role = validated_data.get('role', 'student')

        if role == 'student':
            validated_data['is_active'] = False
            user = User.objects.create_user(password=password or None, **validated_data)
        else:
            user = User.objects.create_user(password=password, **validated_data)

        if role in ROLE_PROFILE_MAP:
            _, ProfileModel, ProfileSerializer = ROLE_PROFILE_MAP[role]
            profile_serializer = ProfileSerializer(data=profile_data)
            profile_serializer.is_valid(raise_exception=True)
            ProfileModel.objects.create(user=user, **profile_serializer.validated_data)

        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Changement de mot de passe — obligatoire à la première connexion."""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})
        return attrs

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value


# ─── JWT ─────────────────────────────────────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Connexion via email — retourne les tokens + les infos utilisateur."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class PendingStudentSerializer(serializers.ModelSerializer):
    """Étudiant en attente de vérification de matricule par un admin."""
    matricule = serializers.SerializerMethodField()
    nationality = serializers.SerializerMethodField()
    current_year = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'date_joined', 'matricule', 'nationality', 'current_year', 'school']

    def get_matricule(self, obj):
        profile = getattr(obj, 'student_profile', None)
        return profile.matricule if profile else None

    def get_nationality(self, obj):
        profile = getattr(obj, 'student_profile', None)
        return profile.nationality if profile else None

    def get_current_year(self, obj):
        profile = getattr(obj, 'student_profile', None)
        return profile.current_year if profile else None

    def get_school(self, obj):
        profile = getattr(obj, 'student_profile', None)
        if profile and profile.school:
            return str(profile.school)
        return None


class UserListSerializer(serializers.ModelSerializer):
    """Lecture seule — utilisée par les admins et modérateurs pour lister les utilisateurs."""
    student_profile = StudentProfileSerializer(read_only=True)
    professional_profile = ProfessionalProfileSerializer(read_only=True)
    researcher_profile = ResearcherProfileSerializer(read_only=True)
    institutional_profile = InstitutionalProfileSerializer(read_only=True)
    staff_profile = StaffProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 'phone', 'avatar', 'is_active', 'date_joined',
            'student_profile', 'professional_profile', 'researcher_profile',
            'institutional_profile', 'staff_profile',
        ]
        read_only_fields = fields
