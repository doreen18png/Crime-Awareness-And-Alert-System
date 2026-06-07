from django import forms
from .models import SOSAlert

class SOSForm(forms.ModelForm):
    class Meta:
        model = SOSAlert
        fields = ['emergency_type', 'message', 'latitude', 'longitude', 'address']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
