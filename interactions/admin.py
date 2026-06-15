from django.contrib import admin

from interactions.models import AdmissionRequest, ContactRequest, InternshipRequest, Lead

# Register your models here.
admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"
admin.site.site_url = None  # Désactive le lien vers le site public depuis l'admin
admin.site.enable_nav_sidebar = False  # Désactive la barre latérale de navigation pour une interface plus épurée   
admin.site.register(Lead)  # Enregistre le modèle Lead pour l'administration
admin.site.register(AdmissionRequest)  # Enregistre le modèle AdmissionRequest pour l'administration
admin.site.register(ContactRequest)  # Enregistre le modèle ContactRequest pour l'administration
admin.site.register(InternshipRequest)  # Enregistre le modèle InternshipRequest pour l'administration
