from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
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
            form.save(commit=True)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return render(request, template, locals())


def logout_view(request):
    logout(request)
    return render(request, 'website/access/registration.html')

