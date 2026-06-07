import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from reports.models import CrimeReport
from emergency.models import SOSAlert


@login_required
def index(request):
    now = timezone.now()
    last_30 = now - timedelta(days=30)
    last_7 = now - timedelta(days=7)

    # Stats cards
    stats = {
        'total_reports': CrimeReport.objects.count(),
        'pending': CrimeReport.objects.filter(status='pending').count(),
        'investigating': CrimeReport.objects.filter(status='investigating').count(),
        'resolved': CrimeReport.objects.filter(status='resolved').count(),
        'active_sos': SOSAlert.objects.filter(status='active').count(),
        'reports_this_week': CrimeReport.objects.filter(created_at__gte=last_7).count(),
        'reports_this_month': CrimeReport.objects.filter(created_at__gte=last_30).count(),
    }

    # Chart: reports by category
    by_category = list(
        CrimeReport.objects.values('category').annotate(count=Count('id')).order_by('-count')
    )

    # Chart: reports per day last 14 days
    by_day = list(
        CrimeReport.objects.filter(created_at__gte=now - timedelta(days=14))
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    for item in by_day:
        item['day'] = item['day'].strftime('%b %d')

    # Chart: by severity
    by_severity = list(
        CrimeReport.objects.values('severity').annotate(count=Count('id'))
    )

    # Recent activity
    recent_reports = CrimeReport.objects.order_by('-created_at')[:8]
    active_alerts = SOSAlert.objects.filter(status='active').order_by('-created_at')[:5]

    # Top crime areas
    top_areas = list(
        CrimeReport.objects.exclude(area='')
        .values('area').annotate(count=Count('id')).order_by('-count')[:5]
    )

    return render(request, 'dashboard/index.html', {
        'stats': stats,
        'by_category_json': json.dumps(by_category),
        'by_day_json': json.dumps(by_day),
        'by_severity_json': json.dumps(by_severity),
        'recent_reports': recent_reports,
        'active_alerts': active_alerts,
        'top_areas': top_areas,
    })


@login_required
def ai_insights(request):
    """Gemini AI-powered crime pattern insights page."""
    from django.conf import settings
    import requests as req

    insights = None
    error = None
    # Prepare summary data for AI
    total = CrimeReport.objects.count()
    pending = CrimeReport.objects.filter(status='pending').count()
    resolved = CrimeReport.objects.filter(status='resolved').count()
    top_categories = list(
        CrimeReport.objects.values('category').annotate(count=Count('id')).order_by('-count')[:5]
    )
    top_areas = list(
        CrimeReport.objects.exclude(area='').values('area').annotate(count=Count('id')).order_by('-count')[:5]
    )
    high_severity = CrimeReport.objects.filter(severity__in=['high', 'critical']).count()

    if request.method == 'POST' or request.GET.get('auto'):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            error = "Gemini API key not configured. Add GEMINI_API_KEY to your environment."
        else:
            custom_query = request.POST.get('query', '')
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                base_context = f"""Crime database summary:
- Total reports: {total}
- Pending: {pending}, Resolved: {resolved}
- High/Critical severity: {high_severity}
- Top categories: {', '.join(f"{c['category']}({c['count']})" for c in top_categories)}
- Top areas: {', '.join(f"{a['area']}({a['count']})" for a in top_areas)}"""

                if custom_query:
                    prompt = f"{base_context}\n\nQuestion from analyst: {custom_query}\nProvide a detailed, structured analysis."
                else:
                    prompt = f"{base_context}\n\nProvide:\n1. Key patterns and trends\n2. High-risk areas and times\n3. Resource allocation recommendations\n4. Preventive strategies\nFormat with clear headers and bullet points."

                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                resp = req.post(url, json=payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    insights = data['candidates'][0]['content']['parts'][0]['text']
                else:
                    error = f"Gemini API error: {resp.status_code}"
            except Exception as e:
                error = f"Error connecting to AI: {str(e)}"

    return render(request, 'dashboard/ai_insights.html', {
        'insights': insights,
        'error': error,
        'total': total,
        'top_categories': top_categories,
        'top_areas': top_areas,
    })
