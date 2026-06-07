from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileForm
from .models import UserProfile
from reports.models import CrimeReport
from emergency.models import SOSAlert


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    recent_reports = CrimeReport.objects.filter(is_public=True).order_by('-created_at')[:5]
    stats = {
        'total_reports': CrimeReport.objects.count(),
        'resolved': CrimeReport.objects.filter(status='resolved').count(),
        'active_alerts': SOSAlert.objects.filter(status='active').count(),
        'communities': UserProfile.objects.count(),
    }
    return render(request, 'core/home.html', {'recent_reports': recent_reports, 'stats': stats})


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone=form.cleaned_data.get('phone', ''),
                badge_number=form.cleaned_data.get('badge_number', ''),
                station=form.cleaned_data.get('station', ''),
            )
            login(request, user)
            messages.success(request, f'Welcome to Vigilant, {user.first_name or user.username}!')
            return redirect('dashboard:index')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            # update user name/email
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('core:profile')
    else:
        form = ProfileForm(instance=profile_obj)
    my_reports = CrimeReport.objects.filter(reporter=request.user).order_by('-created_at')[:10]
    my_alerts = SOSAlert.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'core/profile.html', {'form': form, 'my_reports': my_reports, 'my_alerts': my_alerts})
