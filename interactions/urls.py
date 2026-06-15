# apps/interactions/urls.py
from django.urls import path
from .views import ContactCreateView, AdmissionCreateView, InternshipCreateView, JobOfferListView, JobOfferDetailView

urlpatterns = [
    path('contact/', ContactCreateView.as_view(), name='submit_contact'),
    path('admission/', AdmissionCreateView.as_view(), name='submit_admission'),
    path('internship/', InternshipCreateView.as_view(), name='submit_internship'),
    path('jobs/', JobOfferListView.as_view(), name='job_offer_list'),
    path('jobs/<slug:slug>/', JobOfferDetailView.as_view(), name='job_offer_detail'),
]