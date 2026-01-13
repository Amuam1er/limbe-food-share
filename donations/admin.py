from django.contrib import admin
from .models import Donation, Claim

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['title', 'donor_name', 'donor_type', 'status', 'is_verified', 'expiry_time', 'created_at']
    list_filter = ['status', 'donor_type', 'is_verified', 'created_at']
    search_fields = ['title', 'donor_name', 'donor_phone']
    readonly_fields = ['verification_pin', 'pin_created_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Donor Information', {
            'fields': ('donor_name', 'donor_type', 'donor_phone', 'donor_email')
        }),
        ('Donation Details', {
            'fields': ('title', 'description', 'quantity', 'photo_url')
        }),
        ('Pickup Information', {
            'fields': ('pickup_address', 'latitude', 'longitude', 'pickup_window_start', 'pickup_window_end', 'expiry_time')
        }),
        ('Status & Verification', {
            'fields': ('status', 'is_verified', 'verification_pin', 'pin_created_at', 'created_at', 'updated_at')
        }),
    )

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['volunteer_name', 'donation', 'status', 'phone_revealed', 'claimed_at']
    list_filter = ['status', 'claimed_at']
    search_fields = ['volunteer_name', 'volunteer_phone', 'donation__title']
    readonly_fields = ['claimed_at', 'confirmed_at', 'picked_up_at']