# apps/interactions/urls.py
from django.urls import path
from .views import (
    ContactCreateView, AdmissionCreateView, InternshipCreateView,
    MyAdmissionsView,
    JobOfferListView, JobOfferDetailView,
    LeadListView, LeadDetailView,
    ContactRequestAdminListView, AdmissionRequestAdminListView, InternshipRequestAdminListView, NewsletterBroadcastView, NewsletterSubscribeView, NewsletterUnsubscribeView,
)

urlpatterns = [
    # ── Soumissions publiques ─────────────────────────────────────────────────
    path('contact/', ContactCreateView.as_view(), name='submit_contact'),
    path('admission/', AdmissionCreateView.as_view(), name='submit_admission'),
    path('internship/', InternshipCreateView.as_view(), name='submit_internship'),

    # ── Espace utilisateur ────────────────────────────────────────────────────
    path('admissions/me/', MyAdmissionsView.as_view(), name='my_admissions'),

    # ── Offres d'emploi / stage (lecture publique + CRUD admin) ──────────────
    path('jobs/', JobOfferListView.as_view(), name='job_offer_list'),
    path('jobs/<slug:slug>/', JobOfferDetailView.as_view(), name='job_offer_detail'),

    # ── Gestion admin des leads et demandes ───────────────────────────────────
    path('leads/', LeadListView.as_view(), name='lead_list'),
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead_detail'),
    path('manage/contacts/', ContactRequestAdminListView.as_view(), name='contact_admin_list'),
    path('manage/admissions/', AdmissionRequestAdminListView.as_view(), name='admission_admin_list'),
    path('manage/internships/', InternshipRequestAdminListView.as_view(), name='internship_admin_list'),
    # Nouvelle route Newsletter
    path('newsletter/subscribe/', NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe'),
    path('newsletter/broadcast/', NewsletterBroadcastView.as_view(), name='newsletter_broadcast'),
]