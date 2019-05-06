from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate, login, logout

from .models import User
from .forms import RegistrationForm


class Registration(View):
    template_name = 'website/access/registration.html'

    def get(self, request, *args, **kwargs):
        template = self.template_name
        form = RegistrationForm()
        return render(request, template, locals())

    def post(self, request, *args, **kwargs):
        template = self.template_name
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            user_email = form.cleaned_data['email']

            user_obj = User.objects.get(username=username)

            user = form.save(commit=True)
            user_obj.save()

            user_auth = authenticate(request, username=username, password=password)
        return render(request, template, locals())
