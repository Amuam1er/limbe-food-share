from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Donation, Claim
from .forms import DonationForm, PINVerificationForm, ClaimForm
import cloudinary.uploader

def home(request):
    donations = Donation.objects.filter(
        status='posted',
        is_verified=True,
        expiry_time__gt=timezone.now(),
        pickup_window_end__gt=timezone.now()
    )
    return render(request, 'donations/home.html', {'donations': donations})

def create_donation(request):
    if request.method == 'POST':
        form = DonationForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            
            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                upload_result = cloudinary.uploader.upload(photo)
                donation.photo_url = upload_result['secure_url']
            
            donation.pickup_window_start = timezone.now()
            
            donation.save()
            
            pin = donation.generate_pin()
            send_verification_email(donation, pin)
            
            messages.success(request, f'Donation posted! Check your email ({donation.donor_email}) for verification PIN.')
            return redirect('verify_donation', donation_id=donation.id)
    else:
        form = DonationForm()
    
    return render(request, 'donations/create_donation.html', {'form': form})

def verify_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    
    if donation.is_verified:
        messages.info(request, 'This donation is already verified!')
        return redirect('donation_detail', donation_id=donation.id)
    
    if request.method == 'POST':
        form = PINVerificationForm(request.POST)
        if form.is_valid():
            pin = form.cleaned_data['pin']
            if donation.verify_pin(pin):
                messages.success(request, 'Donation verified! It\'s now visible to volunteers.')
                return redirect('donation_detail', donation_id=donation.id)
            else:
                messages.error(request, 'Invalid or expired PIN. Please check your email.')
    else:
        form = PINVerificationForm()
    
    return render(request, 'donations/verify_donation.html', {
        'form': form,
        'donation': donation
    })

def donation_detail(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    claims = donation.claims.all()
    
    for claim in claims.filter(status='pending'):
        claim.auto_confirm()
    
    return render(request, 'donations/donation_detail.html', {
        'donation': donation,
        'claims': claims
    })

def claim_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    
    if not donation.is_available():
        messages.error(request, 'This donation is no longer available.')
        return redirect('donation_detail', donation_id=donation.id)
    
    active_claim = donation.claims.filter(status__in=['pending', 'confirmed']).first()
    
    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            if active_claim:
                claim = form.save(commit=False)
                claim.donation = donation
                claim.status = 'waitlisted'
                claim.save()
                messages.info(request, 'This donation is being claimed. You\'ve been added to the waitlist.')
            else:
                claim = form.save(commit=False)
                claim.donation = donation
                claim.status = 'pending'
                claim.save()
                
                send_claim_notification(donation, claim)
                
                messages.success(request, f'Claim submitted! Donor notified. You have a 5-minute hold.')
            
            return redirect('donation_detail', donation_id=donation.id)
    else:
        form = ClaimForm()
    
    return render(request, 'donations/claim_donation.html', {
        'form': form,
        'donation': donation,
        'active_claim': active_claim
    })

def confirm_pickup(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    
    if request.method == 'POST':
        claim.status = 'picked_up'
        claim.picked_up_at = timezone.now()
        claim.donation.status = 'picked_up'
        claim.donation.save()
        claim.save()
        
        messages.success(request, 'Pickup confirmed! Thank you for reducing food waste.')
        return redirect('home')
    
    return render(request, 'donations/confirm_pickup.html', {'claim': claim})

def send_verification_email(donation, pin):
    subject = 'Verify Your Food Donation - Limbe Food Share'
    message = f"""
Hello {donation.donor_name},

Thank you for donating food!

Your verification PIN is: {pin}

This PIN will expire in 10 minutes.

Visit this link to verify: http://127.0.0.1:8000/donations/verify/{donation.id}/

Donation Details:
- {donation.title}
- Quantity: {donation.quantity}
- Pickup: {donation.pickup_address}

Thank you for helping reduce food waste in Limbe!

- Limbe Food Share Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [donation.donor_email],
        fail_silently=False,
    )

def send_claim_notification(donation, claim):
    """Notify donor that someone claimed their donation"""
    subject = 'Someone wants your food donation! - Limbe Food Share'
    message = f"""
Hello {donation.donor_name},

Great news! A volunteer wants to pick up your donation:

Donation: {donation.title}
Quantity: {donation.quantity}

Volunteer: {claim.volunteer_name}
Phone: {claim.masked_phone()}

The volunteer has a 5-minute hold. After that, their full contact info will be revealed automatically.

View details: http://127.0.0.1:8000/donations/{donation.id}/

Thank you for reducing food waste!

- Limbe Food Share Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [donation.donor_email],
        fail_silently=False,
    )