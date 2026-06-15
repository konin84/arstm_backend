from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


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
        ('student', 'Étudiant / Candidat'),
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
    must_change_password = models.BooleanField(
        default=False,
        help_text="Oblige l'utilisateur à changer son mot de passe à la prochaine connexion"
    )

    def save(self, *args, **kwargs):
        if not self.username:
            prefix = self.email.split('@')[0] if self.email else 'user'
            self.username = f"{prefix}_{uuid.uuid4().hex[:6]}"
        if self.is_superuser:
            self.must_change_password = False
        super().save(*args, **kwargs)


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
    SECTOR_CHOICES = (
        ('maritime', 'Transport Maritime'),
        ('port', 'Logistique Portuaire'),
        ('offshore', 'Offshore / Industrie Navale'),
        ('security', 'Sûreté et Sécurité Maritime'),
        ('fishing', 'Pêche'),
        ('other', 'Autre'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional_profile')
    company_name = models.CharField(max_length=255, verbose_name="Entreprise / Organisation")
    job_title = models.CharField(max_length=255, verbose_name="Poste occupé")
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default='maritime')
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
    ORG_TYPE_CHOICES = (
        ('ministry', 'Ministère / Administration publique'),
        ('multilateral', 'Organisation Multilatérale (UA, CEDEAO, OMI…)'),
        ('ngo', 'ONG / Fondation'),
        ('private', "Secteur Privé / Fondation d'entreprise"),
        ('other', 'Autre'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='institutional_profile')
    organization_name = models.CharField(max_length=255, verbose_name="Nom de l'organisation")
    position = models.CharField(max_length=255, verbose_name="Fonction / Titre")
    organization_type = models.CharField(max_length=20, choices=ORG_TYPE_CHOICES, default='multilateral')
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
