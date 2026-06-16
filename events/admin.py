
from django.contrib import admin

from events.models import  CompetitionAlertSubscription,Event, PromotionBanner, NewsCategory, NewsPost

# Register your models here.
admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"
admin.site.site_url = None  # Désactive le lien vers le site public depuis l'admin
admin.site.enable_nav_sidebar = False  # Désactive la barre latérale de navigation pour une interface plus épurée   
admin.site.register(Event)  # Enregistre le modèle Event pour l'administration
admin.site.register(PromotionBanner)  # Enregistre le modèle Banner pour l'administration
admin.site.register(CompetitionAlertSubscription)  # Enregistre le modèle NotificationSubscription pour l'administration
admin.site.register(NewsPost)  # Enregistre le modèle NewsPost pour l'administration


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['code', 'label']    