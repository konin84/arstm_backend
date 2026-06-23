from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    UserProfileView,
    AdminCreateUserView,
    ChangePasswordView,
    CustomTokenObtainPairView,
    UsersListView,
    PendingStudentsView,
    ApproveStudentView,
    DeleteUserView,
    SectorListView,
    OrganizationTypeListView,
    TestEmailView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    # Authentification & jetons
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Espace sécurisé utilisateur
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Mot de passe oublié — flux OTP (public)
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Listes de valeurs dynamiques — publiques, pour peupler les formulaires
    path('sectors/', SectorListView.as_view(), name='sector_list'),
    path('organization-types/', OrganizationTypeListView.as_view(), name='organization_type_list'),

    # Administration — création de comptes avec mot de passe temporaire
    path('create/', AdminCreateUserView.as_view(), name='admin_create_user'),

    # Test email — admin uniquement
    path('test-email/', TestEmailView.as_view(), name='test_email'),

    # Administration — liste des utilisateurs et gestion des comptes étudiants
    path('', UsersListView.as_view(), name='users_list'),
    path('pending-students/', PendingStudentsView.as_view(), name='pending_students'),
    path('<int:pk>/approve/', ApproveStudentView.as_view(), name='approve_student'),
    path('<int:pk>/delete/', DeleteUserView.as_view(), name='delete_user'),
]