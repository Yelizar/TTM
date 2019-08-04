from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import check_password
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=128, help_text='You can register with Gmail')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


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
