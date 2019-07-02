from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import TutorDetails, TutorStatus, StudentDetails
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
                if user.role == 'Tutor':
                    TutorStatus.objects.get_or_create(user_id=user.id)
                    obj, created = TutorDetails.objects.get_or_create(user_id=user.id)
                    return redirect(reverse('session:update-tutor-details', kwargs={'pk': obj.user_id}))
                elif user.role == 'Student':
                    StudentDetails.objects.get_or_create(user_id=user.id)
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
            # if user.first_name:
            #     redirect('access:registration2')
            # elif not user.role:
            #     redirect('access:registration3')
            return redirect(reverse('session:profile', kwargs={'pk': user.id}))
        return render(request, template, locals())


def logout_view(request):
    CustomUser.objects.get(id=request.user.id).online_status(online=False)
    logout(request)
    return redirect('access:home')


class HomeView(View):
    template_name = 'website/access/home.html'

    def get(self, request, *args, **kwargs):
        template = self.template_name
        return render(request, template, locals())
