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
)

urlpatterns = [
    # Authentification & jetons
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Espace sécurisé utilisateur
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Administration — création de comptes avec mot de passe temporaire
    path('create/', AdminCreateUserView.as_view(), name='admin_create_user'),

    # Administration — liste des utilisateurs et gestion des comptes étudiants
    path('', UsersListView.as_view(), name='users_list'),
    path('pending-students/', PendingStudentsView.as_view(), name='pending_students'),
    path('<int:pk>/approve/', ApproveStudentView.as_view(), name='approve_student'),
]