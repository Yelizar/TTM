from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import View, UpdateView
from django.contrib.auth import authenticate, login, logout
from .forms import *


class RegistrationView(View):
    template_name = 'website/access/registration_part_1.html'

    def get(self, request):
        form = RegistrationForm()
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            Account.objects.create(website=user)
            return redirect('access:registration2')
        return render(request, self.template_name, locals())


class RegistrationPart2View(View):
    template_name = 'website/access/registration_part_2.html'

    def get(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(pk=request.user.id)
        except CustomUser.DoesNotExist:
            return redirect('access:registration')
        form = RegistrationPart2Form()
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        form = RegistrationPart2Form(request.POST)

        if form.is_valid():
            try:
                user = CustomUser.objects.get(pk=request.user.id)
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.save()
            except CustomUser.DoesNotExist:
                return redirect('access:registration1')
            return redirect(reverse('session:profile', kwargs={'pk': user.id}))
        return render(request, self.template_name, locals())


class LoginView(View):
    template_name = 'website/access/login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('session:profile', kwargs={'pk': user.id}))
        return render(request, self.template_name, locals())


def logout_view(request):
    CustomUser.objects.get(id=request.user.id).online_status(online=False)
    logout(request)
    return redirect('access:home')


class HomeView(View):
    template_name = 'website/access/home.html'

    def get(self, request, *args, **kwargs):
        template = self.template_name
        return render(request, template, locals())


class Application(UpdateView):
    model = Account
    fields = ['native_language', 'phone', 'appear', 'cv']
    template_name = 'website/access/application.html'

    def get_success_url(self):
        return reverse('session:profile', kwargs={'pk': self.object.website.id})

