import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from .models import SOSAlert, SafeZone
from .forms import SOSForm


@login_required
def sos_page(request):
    """Main SOS / emergency page."""
    safe_zones = SafeZone.objects.filter(is_active=True)
    my_alerts = SOSAlert.objects.filter(user=request.user).order_by('-created_at')[:5]
    safe_zones_json = list(safe_zones.values('name', 'zone_type', 'address', 'latitude', 'longitude', 'phone'))
    for z in safe_zones_json:
        z['latitude'] = float(z['latitude'])
        z['longitude'] = float(z['longitude'])
    return render(request, 'emergency/sos.html', {
        'my_alerts': my_alerts,
        'safe_zones_json': json.dumps(safe_zones_json),
    })


@login_required
@require_POST
def trigger_sos(request):
    """AJAX endpoint to trigger an SOS alert."""
    try:
        data = json.loads(request.body)
        alert = SOSAlert.objects.create(
            user=request.user,
            emergency_type=data.get('emergency_type', 'general'),
            message=data.get('message', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            address=data.get('address', ''),
        )
        _run_ai_dispatch(alert)
        return JsonResponse({
            'success': True,
            'alert_id': alert.pk,
            'message': 'SOS alert sent. Help is on the way.',
            'ai_note': alert.ai_dispatch_note,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def alert_list(request):
    """Authority view: list all active alerts."""
    try:
        is_auth = request.user.profile.is_authority
    except Exception:
        is_auth = request.user.is_staff
    if not is_auth:
        messages.error(request, 'Access restricted to authorities.')
        return redirect('core:home')
    alerts = SOSAlert.objects.all()
    status_filter = request.GET.get('status', 'active')
    if status_filter != 'all':
        alerts = alerts.filter(status=status_filter)
    return render(request, 'emergency/alert_list.html', {'alerts': alerts, 'status_filter': status_filter})


@login_required
def alert_detail(request, pk):
    alert = get_object_or_404(SOSAlert, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('response_notes', '')
        if new_status:
            alert.status = new_status
            alert.response_notes = notes
            alert.responding_officer = request.user
            if new_status == 'responding' and not alert.responded_at:
                alert.responded_at = timezone.now()
            elif new_status == 'resolved':
                alert.resolved_at = timezone.now()
            alert.save()
            messages.success(request, f'Alert status updated to {new_status}.')
    return render(request, 'emergency/alert_detail.html', {'alert': alert})


def _run_ai_dispatch(alert):
    """Gemini AI generates a dispatch recommendation."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        prompt = f"""You are an emergency dispatch AI. Generate a brief dispatch note (2-3 sentences) for first responders for this emergency:
Type: {alert.emergency_type}
Message: {alert.message or 'No details provided'}
Location: {alert.address or 'GPS coordinates only'}
Reported by: Verified app user
Keep the note professional, urgent, and actionable."""
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            alert.ai_dispatch_note = text.strip()
            alert.save(update_fields=['ai_dispatch_note'])
    except Exception:
        pass
