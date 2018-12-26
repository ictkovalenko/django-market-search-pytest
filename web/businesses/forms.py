from django import forms
from django.utils import timezone


class ClaimForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form__input form__input_name',
        'placeholder': 'First Name',
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form__input form__input_name',
        'placeholder': 'Last Name',
    }))

    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Email',
    }))

    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Phone',
    }))

    business_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Name of Business',
    }))

    business_address = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Business Address',
    }))


class AnalyticsFilterForm(forms.Form):
    from_date = forms.DateField(required=False)
    to_date = forms.DateField(required=False)

    def clean(self):
        cd = super().clean()
        self.errors.pop('to_date',  None)
        self.errors.pop('from_date',  None)

        if cd.get('to_date'):
            cd['to_date'] = cd['to_date'] + timezone.timedelta(days=1)

        if not cd.get('to_date') and not cd.get('from_date'):
            cd['to_date'] = timezone.now().date() + timezone.timedelta(days=1)
            cd['from_date'] = cd['to_date'] - timezone.timedelta(days=8)

        return cd
