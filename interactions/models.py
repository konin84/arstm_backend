# apps/interactions/models.py
from django.db import models

class Lead(models.Model):
    """
    Modèle centralisant tous les contacts et prospects de la plateforme.
    Essentiel pour mesurer l'objectif KPI de 100 leads qualifiés par mois.
    """
    SOURCE_CHOICES = (
        ('contact', 'Formulaire de Contact général'),
        ('admission', 'Inscription / Admission Concours'),
        ('internship', 'Candidature Stage / Emploi'),
    )
    STATUS_CHOICES = (
        ('new', 'Nouveau'),
        ('contacted', 'En cours de traitement / Contacté'),
        ('converted', 'Converti / Inscrit validé'),
        ('closed', 'Sans suite'),
    )

    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Adresse Email")
    phone = models.CharField(max_length=20, verbose_name="Numéro de Téléphone")
    
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de capture")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_source_display()}) - {self.created_at.strftime('%d/%m/%Y')}"


class ContactRequest(models.Model):
    """Détails spécifiques pour une demande de contact générale"""
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='contact_detail')
    subject = models.CharField(max_length=255, verbose_name="Objet")
    message = models.TextField(verbose_name="Message")

    def __str__(self):
        return f"Message de {self.lead.email} : {self.subject}"


class AdmissionRequest(models.Model):
    """Détails spécifiques pour une pré-inscription ou demande d'admission aux concours"""
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='admission_detail')
    program = models.ForeignKey('academic.Program', on_delete=models.PROTECT, related_name='admissions')
    academic_level = models.CharField(max_length=100, help_text="Ex: Baccalauréat, Licence 2")
    birth_date = models.DateField(verbose_name="Date de naissance")

    def __str__(self):
        return f"Candidature de {self.lead.last_name} pour {self.program.title}"


class InternshipRequest(models.Model):
    """Détails spécifiques pour les dépôts de candidatures (stages ou emplois)"""
    TYPE_CHOICES = (
        ('stage', 'Demande de Stage'),
        ('emploi', 'Candidature Spontanée / Emploi'),
    )
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='internship_detail')
    request_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='stage')
    cv_file = models.FileField(upload_to='interactions/cvs/', verbose_name="Curriculum Vitae (PDF)")
    cover_letter = models.TextField(verbose_name="Lettre de motivation / Message", blank=True, null=True)

    def __str__(self):
        return f"[{self.get_request_type_display()}] {self.lead.first_name} {self.lead.last_name}"


class JobOffer(models.Model):
    """Offres de stage et d'emploi dans le secteur maritime et portuaire"""
    OFFER_TYPE_CHOICES = (
        ('stage', 'Stage'),
        ('emploi', 'Emploi'),
    )

    title = models.CharField(max_length=255, verbose_name="Intitulé du poste")
    slug = models.SlugField(unique=True, blank=True)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES, default='emploi')
    organization = models.CharField(max_length=255, verbose_name="Entreprise / Institution")
    location = models.CharField(max_length=255, verbose_name="Lieu")
    description = models.TextField(verbose_name="Description du poste")
    requirements = models.TextField(verbose_name="Profil recherché / Prérequis", blank=True)
    deadline = models.DateField(verbose_name="Date limite de candidature", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_offer_type_display()}] {self.title} - {self.organization}"