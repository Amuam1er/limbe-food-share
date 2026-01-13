from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import cloudinary.uploader

class Donation(models.Model):
    DONOR_TYPES = [
        ('household', 'Household'),
        ('restaurant', 'Restaurant'),
    ]
    
    STATUS_CHOICES = [
        ('posted', 'Posted'),
        ('claimed', 'Claimed'),
        ('picked_up', 'Picked Up'),
        ('expired', 'Expired'),
    ]
    
    donor_name = models.CharField(max_length=200)
    donor_type = models.CharField(max_length=20, choices=DONOR_TYPES)
    donor_phone = models.CharField(max_length=20)
    donor_email = models.EmailField()
    
    title = models.CharField(max_length=200, help_text="e.g., '5 plates of jollof rice'")
    description = models.TextField(blank=True)
    quantity = models.CharField(max_length=100, help_text="e.g., '5 plates' or '2kg'")
    photo_url = models.URLField(blank=True)
    
    pickup_address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    expiry_time = models.DateTimeField(help_text="When does this food expire?")
    pickup_window_start = models.DateTimeField(default=timezone.now)
    pickup_window_end = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='posted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_verified = models.BooleanField(default=False)
    verification_pin = models.CharField(max_length=4, blank=True)
    pin_created_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.donor_name}"
    
    def is_available(self):
        """Check if donation is still available for claiming"""
        now = timezone.now()
        return (
            self.status == 'posted' 
            and self.is_verified 
            and self.expiry_time > now
            and self.pickup_window_end > now
        )
    
    def generate_pin(self):
        """Generate a 4-digit verification PIN"""
        self.verification_pin = str(random.randint(1000, 9999))
        self.pin_created_at = timezone.now()
        self.save()
        return self.verification_pin
    
    def verify_pin(self, pin):
        """Verify the PIN and activate the donation"""
        if self.verification_pin == pin:
            if timezone.now() - self.pin_created_at < timedelta(minutes=10):
                self.is_verified = True
                self.save()
                return True
        return False


class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending (5-min hold)'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
    ]
    
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='claims')
    
    volunteer_name = models.CharField(max_length=200)
    volunteer_phone = models.CharField(max_length=20)
    volunteer_email = models.EmailField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    claimed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    
    phone_revealed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['claimed_at']
    
    def __str__(self):
        return f"{self.volunteer_name} -> {self.donation.title}"
    
    def is_hold_expired(self):
        """Check if 5-minute hold has expired"""
        if self.status == 'pending':
            return timezone.now() - self.claimed_at > timedelta(minutes=5)
        return False
    
    def auto_confirm(self):
        if self.is_hold_expired() and self.status == 'pending':
            self.status = 'confirmed'
            self.confirmed_at = timezone.now()
            self.phone_revealed = True
            self.donation.status = 'claimed'
            self.donation.save()
            self.save()
            return True
        return False
    
    def masked_phone(self):
        if self.phone_revealed or self.status in ['confirmed', 'picked_up']:
            return self.volunteer_phone
        if len(self.volunteer_phone) > 6:
            return self.volunteer_phone[:3] + '***' + self.volunteer_phone[-3:]
        return '***'