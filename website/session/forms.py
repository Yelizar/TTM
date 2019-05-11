from django import forms


class TutorStatusForm(forms.Form):

    is_active = forms.CharField(label='Actions', widget=forms.RadioSelect(
                                choices={('1', 'Active'), ('0', 'Do not disturb')}))
