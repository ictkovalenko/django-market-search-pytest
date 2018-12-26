from django import forms
from django.contrib.auth.forms import UserCreationForm as OriginalUserCreationForm

from .models import User


class UserCreationForm(OriginalUserCreationForm):
    agree_terms = forms.BooleanField()
    name = forms.CharField(max_length=25)

    class Meta:
        model = User
        fields = ('name', 'first_name', 'last_name', 'email', 'is_age_verified')
