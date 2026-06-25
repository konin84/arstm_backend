from django.contrib import admin

from interactions.models import AdmissionRequest, ContactRequest, InternshipRequest, Lead, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Logo", {"fields": ("logo",)}),
        ("Réseaux sociaux", {"fields": ("facebook", "twitter", "linkedin", "instagram", "youtube", "whatsapp")}),
    )

    def has_add_permission(self, _request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, _request, _obj=None):
        return False

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
