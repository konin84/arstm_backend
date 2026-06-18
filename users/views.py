from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .utils import send_welcome_email, generate_temp_password
from django.shortcuts import get_object_or_404
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserListSerializer,
    AdminCreateUserSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    PendingStudentSerializer,
    SectorSerializer,
    OrganizationTypeSerializer,
    RESTRICTED_ROLES,
)
from .models import Sector, OrganizationType
from .permissions import IsAdmin, IsAdminOrModerator

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Connexion via email ou téléphone — retourne les tokens + les infos utilisateur."""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """Inscription publique — rôles admin et modérateur exclus. Mot de passe généré automatiquement."""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.role != 'student':
            send_welcome_email(user, user._temp_password)
        headers = self.get_success_headers(serializer.data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Récupération et mise à jour du profil de l'utilisateur connecté."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class AdminCreateUserView(generics.CreateAPIView):
    """
    Création de compte par un administrateur.
    Génère un mot de passe temporaire envoyé par email.
    Seul l'admin peut créer des comptes modérateur ou admin.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    serializer_class = AdminCreateUserSerializer

    def create(self, request, *args, **kwargs):
        role = request.data.get('role', 'student')
        if role in RESTRICTED_ROLES and not request.user.role == 'admin':
            return Response(
                {"detail": "Seul un administrateur peut créer un compte modérateur ou administrateur."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.role != 'student':
            send_welcome_email(user, user._temp_password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    """
    Changement de mot de passe — obligatoire à la première connexion.
    Réinitialise must_change_password=False après un changement réussi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.must_change_password = False
        user.save()

        return Response(
            {"detail": "Mot de passe modifié avec succès."},
            status=status.HTTP_200_OK,
        )


class UsersListView(generics.ListAPIView):
    """Liste de tous les utilisateurs — accessible aux admins et modérateurs."""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrModerator]
    serializer_class = UserListSerializer

    def get_queryset(self):
        return User.objects.select_related(
            'student_profile', 'professional_profile',
            'researcher_profile', 'institutional_profile', 'staff_profile',
        ).order_by('-date_joined')


class PendingStudentsView(generics.ListAPIView):
    """Liste des étudiants en attente de vérification — accessible aux admins et modérateurs."""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrModerator]
    serializer_class = PendingStudentSerializer

    def get_queryset(self):
        return User.objects.filter(role='student', is_active=False).select_related('student_profile__school')


class DeleteUserView(APIView):
    """Suppression d'un compte utilisateur — réservée aux administrateurs."""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            return Response(
                {"detail": "Vous ne pouvez pas supprimer votre propre compte."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApproveStudentView(APIView):
    """Activation du compte étudiant après vérification du matricule — accessible aux admins et modérateurs."""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrModerator]

    def post(self, request, pk):
        student = get_object_or_404(User, pk=pk, role='student')

        if student.is_active:
            return Response(
                {"detail": "Ce compte est déjà actif."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        temp_password = generate_temp_password()
        student.set_password(temp_password)
        student.is_active = True
        student.must_change_password = True
        student.save(update_fields=['password', 'is_active', 'must_change_password'])

        send_welcome_email(student, temp_password)

        return Response(
            {
                "detail": "Compte étudiant activé avec succès.",
                "user": UserSerializer(student).data,
            },
            status=status.HTTP_200_OK,
        )


# ─── Test email ─────────────────────────────────────────────────────────────

class TestEmailView(APIView):
    """Envoie un email de test synchrone — réservé aux administrateurs."""
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request):
        recipient = (
            request.data.get('recipient')
            or getattr(settings, 'TEST_EMAIL_RECIPIENT', '')
            or request.user.email
        )
        try:
            send_mail(
                subject='[ARSTM] Email de test',
                message='Cet email confirme que l\'envoi d\'emails fonctionne correctement.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception as e:
            return Response({'detail': f'Échec : {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': f'Email envoyé à {recipient}.'}, status=status.HTTP_200_OK)


# ─── Listes de valeurs dynamiques ──────────────────────────────────────────

class SectorListView(generics.ListAPIView):
    """Endpoint public — secteurs d'activité disponibles pour le profil Professionnel/Recruteur."""
    queryset = Sector.objects.filter(is_active=True)
    serializer_class = SectorSerializer
    permission_classes = [permissions.AllowAny]


class OrganizationTypeListView(generics.ListAPIView):
    """Endpoint public — types d'organisation disponibles pour le profil Bailleur de fonds."""
    queryset = OrganizationType.objects.filter(is_active=True)
    serializer_class = OrganizationTypeSerializer
    permission_classes = [permissions.AllowAny]
