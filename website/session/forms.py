from django import forms
from django.utils.translation import gettext_lazy as _


class SessionCompletionForm(forms.Form):
    rate = forms.IntegerField(label="Session rate", max_value=5, min_value=0, help_text="By default 5")
    confirmed = forms.BooleanField(label="Did session held?")
    comment = forms.CharField(widget=forms.Textarea)
