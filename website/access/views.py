from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from .forms import *


class RegistrationView(View):
    template_name = 'website/access/registration_part_1.html'

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

        return redirect('access:registration2')


class RegistrationPart2View(View):
    template_name = 'website/access/registration_part_2.html'

    def get(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(pk=request.user.id)
        except CustomUser.DoesNotExist:
            return redirect('access:registration')
        template = self.template_name
        form = RegistrationPart2Form()
        return render(request, template, locals())

    def post(self, request, *args, **kwargs):
        template = self.template_name
        form = RegistrationPart2Form(request.POST)

        if form.is_valid():
            try:
                user = CustomUser.objects.get(pk=request.user.id)
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.save()
            except CustomUser.DoesNotExist:
                return redirect('access:registration1')
        return redirect('access:registration3')


class RegistrationPart3View(View):
    template_name = 'website/access/registration_part_3.html'

    def get(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(pk=request.user.id)
            if not user.first_name:
                return redirect('access:registration2')
            if user.role:
                return redirect('access:home')
        except CustomUser.DoesNotExist:
            return redirect('access:registration')
        template = self.template_name
        form = RegistrationPart3Form()
        return render(request, template, locals())

    def post(self, request, *args, **kwargs):
        template = self.template_name
        form = RegistrationPart3Form(request.POST)
        if form.is_valid():
            try:
                user = CustomUser.objects.get(pk=request.user.id)
                user.role = form.cleaned_data.get('role')
                user.save()
                return redirect('access:home')
            except CustomUser.DoesNotExist:
                print("Error")
        return redirect('access:registration3')


class LoginView(View):
    template_name = 'website/access/login.html'

    def get(self, request, *args, **kwargs):
        template = self.template_name
        form = LoginForm()
        return render(request, template, locals())

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        template = self.template_name
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('access:home')
        return render(request, template, locals())


def logout_view(request):
    logout(request)
    return redirect('access:home')


class HomeView(View):
    template_name = 'website/access/home.html'

    def get(self, request, *args, **kwargs):
        template = self.template_name
        return render(request, template, locals())
