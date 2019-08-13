from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import View
from .utils import *

from .forms import SessionCompletionForm, InitializeForm
from .models import *


class ProfileDetailsView(LoginRequiredMixin, View):
    template_name = 'website/session/profile.html'
    login_url = 'access:login'
    redirect_field_name = 'login_required'
    now = timezone.now()

    def get(self, request, *args, **kwargs):
        obj = Account.objects.get(website_id=kwargs['pk'])
        if 'student' in kwargs:
            student = Account.objects.get(id=kwargs['student'])
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        obj = Account.objects.get(website_id=kwargs['pk'])
        return render(request, self.template_name, locals())


class SessionView(View):
    template_name = 'website/session/session.html'

    def get(self, request):
        obj = Account.objects.get(website=request.user)
        try:
            session = Session.objects.get(student_id=obj.id, is_active=True)
        except Session.DoesNotExist:
            form = InitializeForm()
        return render(request, self.template_name, locals())

    def post(self, request):
        form = InitializeForm(request.POST)
        obj = Account.objects.get(website=request.user)
        if 'cancel' in request.POST:
            # Use save() method to call signal
            session = Session.objects.get(student=obj, is_active=True)
            session.is_active = False
            session.save()
            form = InitializeForm()
        elif form.is_valid():
            language = form.cleaned_data.get('language')
            session, _ = Session.objects.get_or_create(student=obj, language=language, is_active=True)
            del form
        return render(request, self.template_name, locals())


class HistoryView(View):
    template_name = 'website/session/history.html'

    def get(self, request):
        obj = Account.objects.get(website=request.user)
        history = Session.objects.filter(student_id=obj.id)
        return render(request, self.template_name, locals())


class SessionCompletion(View):
    template_name = 'website/session/session_completion.html'

    def get(self, request, *args, **kwargs):
        form = SessionCompletionForm()
        object = Session.objects.get(id=kwargs['session_id'])
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        form = SessionCompletionForm(request.POST)
        if form.is_valid():
            try:
                session = Session.objects.get(id=kwargs['session_id'])
                # should be rebuild
                if request.user.role == 'Student':
                    session.student_confirm = form.cleaned_data.get('confirmed')
                if session.student_confirm:
                    session.is_going = False
                session.rate = form.cleaned_data.get('rate')
                session.save()
                return redirect(reverse('session:profile', kwargs={'pk': request.user.id}))
            except ValueError:
                redirect('website/session/404.html')
        else:
            return redirect('access:home')


def connect_view(request, **kwargs):
    if request.method == 'GET':
        tutor = get_user_model().objects.get(account__id=request.user.id)
        student = Account.objects.get(website_id=kwargs['pk'])
        # notice_student_website(tutor=tutor, student=student)
        return HttpResponseRedirect(
            reverse('session:profile_action', kwargs={'pk': request.user.id, 'student': student.id}))
