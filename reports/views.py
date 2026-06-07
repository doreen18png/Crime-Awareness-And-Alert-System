import json
import os
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import CrimeReport, ReportComment
from .forms import CrimeReportForm, CommentForm


def report_list(request):
    reports = CrimeReport.objects.filter(is_public=True)
    category = request.GET.get('category')
    severity = request.GET.get('severity')
    status = request.GET.get('status')
    if category:
        reports = reports.filter(category=category)
    if severity:
        reports = reports.filter(severity=severity)
    if status:
        reports = reports.filter(status=status)
    # For map: all public reports with coordinates
    map_reports = list(reports.filter(latitude__isnull=False).values(
        'id', 'title', 'category', 'severity', 'status',
        'latitude', 'longitude', 'address', 'created_at'
    ))
    for r in map_reports:
        r['latitude'] = float(r['latitude'])
        r['longitude'] = float(r['longitude'])
        r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M')
    return render(request, 'reports/list.html', {
        'reports': reports,
        'map_reports_json': json.dumps(map_reports),
        'categories': CrimeReport.CATEGORY_CHOICES,
        'severities': CrimeReport.SEVERITY_CHOICES,
        'statuses': CrimeReport.STATUS_CHOICES,
        'selected_category': category,
        'selected_severity': severity,
        'selected_status': status,
    })


def report_detail(request, pk):
    report = get_object_or_404(CrimeReport, pk=pk)
    comments = report.comments.all()
    comment_form = CommentForm()
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.report = report
            c.author = request.user
            try:
                c.is_official = request.user.profile.is_authority
            except Exception:
                c.is_official = False
            c.save()
            messages.success(request, 'Comment added.')
            return redirect('reports:detail', pk=pk)
    return render(request, 'reports/detail.html', {
        'report': report,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def submit_report(request):
    if request.method == 'POST':
        form = CrimeReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            if form.cleaned_data.get('anonymous'):
                report.anonymous = True
            report.save()
            # Trigger Gemini AI analysis async (simple call)
            _run_ai_analysis(report)
            messages.success(request, 'Report submitted successfully. Thank you for keeping your community safe.')
            return redirect('reports:detail', pk=report.pk)
    else:
        form = CrimeReportForm()
    return render(request, 'reports/submit.html', {'form': form})


@login_required
def my_reports(request):
    reports = CrimeReport.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'reports/my_reports.html', {'reports': reports})


def _run_ai_analysis(report):
    """Call Gemini API to analyze the crime report."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        prompt = f"""Analyze this crime report and respond ONLY with a JSON object with these keys:
- summary: a concise 2-sentence summary for authorities
- risk_score: integer 1-100 indicating severity/urgency  
- recommendations: 2-3 bullet points of recommended actions for police

Report details:
Title: {report.title}
Category: {report.category}
Severity: {report.severity}
Description: {report.description}
Location: {report.address or 'Unknown'}"""

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            # strip code fences
            text = text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
            parsed = json.loads(text)
            report.ai_summary = parsed.get('summary', '')
            report.ai_risk_score = int(parsed.get('risk_score', 0))
            report.ai_recommendations = parsed.get('recommendations', '')
            report.save(update_fields=['ai_summary', 'ai_risk_score', 'ai_recommendations'])
    except Exception:
        pass  # AI analysis is best-effort


def api_reports_geojson(request):
    """API endpoint returning reports as GeoJSON for map."""
    reports = CrimeReport.objects.filter(is_public=True, latitude__isnull=False)
    features = []
    for r in reports:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(r.longitude), float(r.latitude)]},
            "properties": {
                "id": r.pk,
                "title": r.title,
                "category": r.category,
                "severity": r.severity,
                "status": r.status,
                "address": r.address,
                "date": r.created_at.strftime('%b %d, %Y'),
                "url": f"/reports/{r.pk}/",
                "color": r.get_severity_color(),
            }
        })
    return JsonResponse({"type": "FeatureCollection", "features": features})
