
from django.contrib import admin

from events.models import  CompetitionAlertSubscription,Event, PromotionBanner

# Register your models here.
admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"
admin.site.site_url = None  # Désactive le lien vers le site public depuis l'admin
admin.site.enable_nav_sidebar = False  # Désactive la barre latérale de navigation pour une interface plus épurée   
admin.site.register(Event)  # Enregistre le modèle Event pour l'administration
admin.site.register(PromotionBanner)  # Enregistre le modèle Banner pour l'administration
admin.site.register(CompetitionAlertSubscription)  # Enregistre le modèle NotificationSubscription pour l'administration    