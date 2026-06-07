from django.db import models
from django.contrib.auth.models import User


class SOSAlert(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active — Needs Response'),
        ('responding', 'Responding'),
        ('resolved', 'Resolved'),
        ('false_alarm', 'False Alarm'),
    ]
    EMERGENCY_TYPE_CHOICES = [
        ('general', 'General Emergency'),
        ('assault', 'Assault / Attack'),
        ('medical', 'Medical Emergency'),
        ('fire', 'Fire'),
        ('accident', 'Accident'),
        ('kidnap', 'Kidnapping'),
        ('robbery', 'Robbery in Progress'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos_alerts')
    emergency_type = models.CharField(max_length=30, choices=EMERGENCY_TYPE_CHOICES, default='general')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.CharField(max_length=300, blank=True)

    # Response
    responding_officer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responding_alerts'
    )
    response_notes = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # AI Dispatch note
    ai_dispatch_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SOS [{self.emergency_type}] by {self.user.username} — {self.status}"


class SafeZone(models.Model):
    ZONE_TYPE_CHOICES = [
        ('police_station', 'Police Station'),
        ('hospital', 'Hospital'),
        ('fire_station', 'Fire Station'),
        ('community_center', 'Community Center'),
        ('school', 'School'),
    ]
    name = models.CharField(max_length=200)
    zone_type = models.CharField(max_length=30, choices=ZONE_TYPE_CHOICES)
    address = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.zone_type})"
