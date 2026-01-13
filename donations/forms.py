from django import forms
from .models import Donation, Claim
from datetime import datetime, timedelta
from django.utils import timezone

class DonationForm(forms.ModelForm):
    photo = forms.ImageField(required=False, help_text="Upload a photo of the food")
    
    class Meta:
        model = Donation
        fields = [
            'donor_name', 'donor_type', 'donor_phone', 'donor_email',
            'title', 'description', 'quantity',
            'pickup_address', 'expiry_time', 'pickup_window_end'
        ]
        widgets = {
            'donor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'donor_type': forms.Select(attrs={'class': 'form-control'}),
            'donor_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 237123456789'}),
            'donor_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5 plates of jollof rice'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: Any special notes?'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5 plates or 2kg'}),
            'pickup_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full pickup address'}),
            'expiry_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'pickup_window_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'donor_name': 'Your Name',
            'donor_type': 'I am a',
            'donor_phone': 'Phone Number',
            'donor_email': 'Email Address',
            'title': 'What food are you donating?',
            'description': 'Additional Details',
            'quantity': 'How much?',
            'pickup_address': 'Pickup Address',
            'expiry_time': 'Food expires on',
            'pickup_window_end': 'Available for pickup until',
        }

class PINVerificationForm(forms.Form):
    pin = forms.CharField(
        max_length=4, 
        min_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '0000',
            'style': 'font-size: 24px; letter-spacing: 10px;'
        }),
        label='Enter 4-digit PIN'
    )

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['volunteer_name', 'volunteer_phone', 'volunteer_email']
        widgets = {
            'volunteer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'volunteer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 237123456789'}),
            'volunteer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com (optional)'}),
        }
        labels = {
            'volunteer_name': 'Your Name',
            'volunteer_phone': 'Your Phone Number',
            'volunteer_email': 'Your Email (Optional)',
        }