from django.contrib import admin

from academic.models import Document, Domain, Program, ProgramType, Regime

# Register your models here.
admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"
admin.site.site_url = None  # Désactive le lien vers le site public depuis l'admin
admin.site.enable_nav_sidebar = False  # Désactive la barre latérale de navigation pour une interface plus épurée   
admin.site.register(Domain) # Enregistre le modèle Domain pour l'administration
admin.site.register(Program)  # Enregistre le modèle Program pour l'administration
admin.site.register(Document)  # Enregistre le modèle Program pour l'administration


@admin.register(ProgramType)
class ProgramTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['code', 'label']


@admin.register(Regime)
class RegimeAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['code', 'label']