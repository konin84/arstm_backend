from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from users.models import StudentProfile, User
from users.utils import generate_temp_password, send_welcome_email

admin.site.site_header = "ARSTM - Administration"
admin.site.site_title = "ARSTM - Admin"
admin.site.index_title = "Tableau de bord de l'administration ARSTM"
admin.site.site_url = None
admin.site.enable_nav_sidebar = False


def approve_students(modeladmin, request, queryset):
    pending = queryset.filter(role='student', is_active=False)
    count = 0
    for student in pending:
        temp_password = generate_temp_password()
        student.set_password(temp_password)
        student.is_active = True
        student.must_change_password = True
        student.save(update_fields=['password', 'is_active', 'must_change_password'])
        send_welcome_email(student, temp_password)
        count += 1
    modeladmin.message_user(request, f"{count} compte(s) étudiant(s) activé(s) et identifiants envoyés par email.")

approve_students.short_description = "Activer les comptes étudiants sélectionnés"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'account_status', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    actions = [approve_students]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Rôle et statut', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'must_change_password')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    def account_status(self, obj):
        if obj.role == 'student' and not obj.is_active:
            return format_html('<span style="color:orange;font-weight:bold;">En attente de vérification</span>')
        if obj.is_active:
            return format_html('<span style="color:green;">Actif</span>')
        return format_html('<span style="color:red;">Désactivé</span>')

    account_status.short_description = "Statut"


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'matricule', 'school', 'current_year', 'account_active']
    list_filter = ['school', 'user__is_active']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'matricule']
    raw_id_fields = ['user']

    def account_active(self, obj):
        return obj.user.is_active

    account_active.boolean = True
    account_active.short_description = "Compte actif"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'school')
