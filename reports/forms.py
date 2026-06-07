from django import forms
from .models import CrimeReport, ReportComment


class CrimeReportForm(forms.ModelForm):
    anonymous = forms.BooleanField(required=False, label='Submit anonymously')

    class Meta:
        model = CrimeReport
        fields = ['title', 'description', 'category', 'severity', 'address', 'area',
                  'latitude', 'longitude', 'image', 'is_public', 'anonymous']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = ReportComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'})
        }
