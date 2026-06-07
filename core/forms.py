from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial='citizen')
    badge_number = forms.CharField(max_length=50, required=False, help_text='Officers only')
    station = forms.CharField(max_length=100, required=False, help_text='Officers only')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ('phone', 'badge_number', 'station', 'avatar')
