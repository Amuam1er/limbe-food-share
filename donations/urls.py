from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('donate/', views.create_donation, name='create_donation'),
    path('verify/<int:donation_id>/', views.verify_donation, name='verify_donation'),
    path('donations/<int:donation_id>/', views.donation_detail, name='donation_detail'),
    path('donations/<int:donation_id>/claim/', views.claim_donation, name='claim_donation'),
    path('claims/<int:claim_id>/confirm/', views.confirm_pickup, name='confirm_pickup'),
]