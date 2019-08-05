from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    username = forms.CharField(label='Username', min_length=4, max_length=150)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        e = CustomUser.objects.filter(email=email)
        if e.count():
            raise ValidationError("Email already exists")
        return email


class RegistrationPart2Form(forms.Form):
    first_name = forms.CharField( help_text='Please type your first name', max_length=30)
    last_name = forms.CharField(help_text='Please type your last name', max_length=150)


class LoginForm(forms.ModelForm):
    password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            raise forms.ValidationError("Please insert your user name")
        try:
            CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError("User does not exist")
        return username
