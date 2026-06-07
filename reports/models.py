from django.db import models
from django.contrib.auth.models import User


class CrimeReport(models.Model):
    CATEGORY_CHOICES = [
        ('theft', 'Theft / Robbery'),
        ('assault', 'Assault / Violence'),
        ('vandalism', 'Vandalism'),
        ('fraud', 'Fraud / Scam'),
        ('drug', 'Drug Activity'),
        ('suspicious', 'Suspicious Activity'),
        ('traffic', 'Traffic Incident'),
        ('missing', 'Missing Person'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    anonymous = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_public = models.BooleanField(default=True)

    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.CharField(max_length=300, blank=True)
    area = models.CharField(max_length=100, blank=True)

    # Media
    image = models.ImageField(upload_to='reports/', blank=True, null=True)

    # AI Analysis
    ai_summary = models.TextField(blank=True)
    ai_risk_score = models.IntegerField(null=True, blank=True)
    ai_recommendations = models.TextField(blank=True)

    # Authority response
    assigned_officer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_reports'
    )
    officer_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category}] {self.title} — {self.status}"

    def get_severity_color(self):
        return {
            'low': '#22c55e',
            'medium': '#f59e0b',
            'high': '#ef4444',
            'critical': '#7c3aed',
        }.get(self.severity, '#gray')


class ReportComment(models.Model):
    report = models.ForeignKey(CrimeReport, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_official = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.report}"
