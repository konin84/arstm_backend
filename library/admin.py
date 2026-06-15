from django.contrib import admin

from library.models import ResearchPaper, SectorWatch

# Register your models here.
admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"
admin.site.site_url = None  # Désactive le lien vers le site public depuis l'admin
admin.site.enable_nav_sidebar = False  # Désactive la barre latérale de navigation pour une interface plus épurée   
admin.site.register(SectorWatch)  # Enregistre le modèle SectorWatch pour l'administration
admin.site.register(ResearchPaper)  # Enregistre le modèle ResearchPaper pour l'administration