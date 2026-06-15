from django.urls import path
from .views import (
    SchoolListView, SchoolDetailView,
    InfrastructureListView, InfrastructureDetailView,
    PartnerListView, PartnerDetailView,
    TestimonialListView, TestimonialDetailView,
)

urlpatterns = [
    path('schools/', SchoolListView.as_view(), name='school_list'),
    path('schools/<slug:slug>/', SchoolDetailView.as_view(), name='school_detail'),

    path('infrastructures/', InfrastructureListView.as_view(), name='infrastructure_list'),
    path('infrastructures/<int:pk>/', InfrastructureDetailView.as_view(), name='infrastructure_detail'),

    path('partners/', PartnerListView.as_view(), name='partner_list'),
    path('partners/<int:pk>/', PartnerDetailView.as_view(), name='partner_detail'),

    path('testimonials/', TestimonialListView.as_view(), name='testimonial_list'),
    path('testimonials/<int:pk>/', TestimonialDetailView.as_view(), name='testimonial_detail'),
]