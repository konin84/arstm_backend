from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from institution.models import Infrastructure, Partner, PartnerType, School, DirectorMessage

admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"
admin.site.site_url = None
admin.site.enable_nav_sidebar = False


@admin.register(School)
class SchoolAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Infrastructure)
class InfrastructureAdmin(TranslationAdmin):
    pass


@admin.register(DirectorMessage)
class DirectorMessageAdmin(TranslationAdmin):
    pass


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    pass


@admin.register(PartnerType)
class PartnerTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['code', 'label']