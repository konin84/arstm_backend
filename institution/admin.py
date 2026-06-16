from django.contrib import admin

from institution.models import Infrastructure, Partner, PartnerType, School, DirectorMessage

# Register your models here.
admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"    
admin.site.site_url = None  # Désactive le lien vers le site public depuis l'admin
admin.site.enable_nav_sidebar = False  # Désactive la barre latérale de navigation pour une interface plus épurée
admin.site.register(School)  # Enregistre le modèle School pour l'administration
admin.site.register(Infrastructure)  # Enregistre le modèle Infrastructure pour l'administration
admin.site.register(Partner)  # Enregistre le modèle Partner pour l'administration
admin.site.register(DirectorMessage)  # Enregistre le modèle DirectorMessage pour l'administration


@admin.register(PartnerType)
class PartnerTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['code', 'label']