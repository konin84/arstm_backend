from django.contrib import admin

from forum.models import Category, Post, Topic

# Register your models here.
admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"
admin.site.site_url = None  # Désactive le lien vers le site public depuis l'admin
admin.site.enable_nav_sidebar = False  # Désactive la barre latérale de navigation pour une interface plus épurée   
admin.site.register(Category)  # Enregistre le modèle Category pour l'administration
admin.site.register(Topic)  # Enregistre le modèle Topic pour l'administration
admin.site.register(Post)  # Enregistre le modèle Post pour l'administration