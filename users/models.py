from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class LookupValue(models.Model):
    """
    Base abstraite pour les listes de valeurs éditables depuis l'admin sans
    déploiement (secteur, type d'organisation, titre académique, etc.).
    `code` est la valeur stable utilisée par l'API et le frontend ;
    `label` est le texte affiché (modifiable librement par un admin).
    """
    code = models.SlugField(max_length=30, unique=True)
    label = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['order', 'label']

    def __str__(self):
        return self.label


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields['must_change_password'] = False
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Candidat / Postulant'),
        ('student', 'Étudiant'),
        ('professional', 'Professionnel / Entreprise'),
        ('recruiter', 'Recruteur / Partenaire RH'),
        ('donor', 'Bailleur de fonds / Partenaire Institutionnel'),
        ('researcher', 'Chercheur / Expert Maritime'),
        ('moderator', 'Modérateur ARSTM'),
        ('admin', 'Administrateur / Agent ARSTM (DCM)'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name="Photo de profil")
    must_change_password = models.BooleanField(
        default=False,
        help_text="Oblige l'utilisateur à changer son mot de passe à la prochaine connexion"
    )
    receive_competition_notifications = models.BooleanField(
        default=True,
        help_text="L'utilisateur reçoit les emails lors de l'ouverture d'un nouveau concours"
    )

    def save(self, *args, **kwargs):
        if not self.username:
            prefix = self.email.split('@')[0] if self.email else 'user'
            self.username = f"{prefix}_{uuid.uuid4().hex[:6]}"
        if self.is_superuser:
            self.must_change_password = False
        if self.pk:
            old_avatar = User.objects.filter(pk=self.pk).values_list('avatar', flat=True).first()
            if old_avatar and old_avatar != self.avatar.name:
                self.avatar.storage.delete(old_avatar)
        super().save(*args, **kwargs)


# ─── Listes de valeurs dynamiques ───────────────────────────────────────────

class Sector(LookupValue):
    """Secteur d'activité (Professionnel / Recruteur)."""


class OrganizationType(LookupValue):
    """Type d'organisation (Bailleur de fonds / Partenaire institutionnel)."""


# ─── Profils par rôle ────────────────────────────────────────────────────────

class StudentProfile(models.Model):
    """Étudiant / Candidat — informations académiques"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    school = models.ForeignKey('institution.School', on_delete=models.SET_NULL, null=True)
    matricule = models.CharField(max_length=50, unique=True, blank=True)
    current_year = models.CharField(max_length=50, blank=True, help_text="Ex : Licence 2, Master 1")
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Étudiant : {self.user.get_full_name()} ({self.matricule})"


class ProfessionalProfile(models.Model):
    """Professionnel / Entreprise et Recruteur / Partenaire RH"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional_profile')
    company_name = models.CharField(max_length=255, verbose_name="Entreprise / Organisation")
    job_title = models.CharField(max_length=255, verbose_name="Poste occupé")
    sector = models.ForeignKey(Sector, on_delete=models.PROTECT, null=True, blank=True, related_name='professional_profiles')
    country = models.CharField(max_length=100, verbose_name="Pays")
    company_website = models.URLField(blank=True, null=True, verbose_name="Site web (recruteurs)")

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.job_title} @ {self.company_name}"


class ResearcherProfile(models.Model):
    """Chercheur / Expert Maritime"""
    TITLE_CHOICES = (
        ('dr', 'Dr.'),
        ('prof', 'Prof.'),
        ('mr', 'M.'),
        ('ms', 'Mme'),
        ('ml', 'Mle'),
        ('eng', 'Ing.'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='researcher_profile')
    academic_title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='dr')
    institution = models.CharField(max_length=255, verbose_name="Institution / Laboratoire")
    specialization = models.ForeignKey(
        'academic.Domain',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Domaine de spécialisation"
    )
    country = models.CharField(max_length=100, verbose_name="Pays")
    research_profile_url = models.URLField(blank=True, null=True, verbose_name="Profil ORCID / ResearchGate")

    def __str__(self):
        return f"{self.get_academic_title_display()} {self.user.get_full_name()} — {self.institution}"


class InstitutionalProfile(models.Model):
    """Bailleur de fonds / Partenaire Institutionnel"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='institutional_profile')
    organization_name = models.CharField(max_length=255, verbose_name="Nom de l'organisation")
    position = models.CharField(max_length=255, verbose_name="Fonction / Titre")
    organization_type = models.ForeignKey(OrganizationType, on_delete=models.PROTECT, null=True, blank=True, related_name='institutional_profiles')
    country = models.CharField(max_length=100, verbose_name="Pays")

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.position} @ {self.organization_name}"


class StaffProfile(models.Model):
    """Administrateur / Agent ARSTM — créé par le superadmin uniquement"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    department = models.CharField(max_length=255, verbose_name="Département / Direction")
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="Matricule agent")

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.department}"


class PasswordResetOTP(models.Model):
    """Code OTP à 6 chiffres envoyé par email pour réinitialiser un mot de passe oublié."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_otps')
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
