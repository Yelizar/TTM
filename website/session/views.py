from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import *
from .forms import SessionCompletionForm, InitializeForm
from notifications.signals import notify
from django.utils.html import format_html


class ProfileDetailsView(LoginRequiredMixin, View):
    template_name = 'website/session/profile.html'
    login_url = 'access:login'
    redirect_field_name = 'login_required'
    now = timezone.now()

    def get(self, request, *args, **kwargs):
        obj = Account.objects.get(website_id=kwargs['pk'])
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
            Session.objects.filter(student=obj, is_active=True).update(is_active=False)
            form = InitializeForm()
        elif form.is_valid():
            language = form.cleaned_data.get('language')
            session = Session.objects.get_or_create(student=obj, language=language, is_active=True)
            form = None
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
        student = Account.objects.get(website_id=kwargs['pk'])
        tutor = request.user
        url = tutor.get_absolute_url()
        verb = format_html("<a href='{url}'> Check tutor </a>".format(url=url))
        notify.send(sender=tutor, recipient=student.website, verb=verb,
                    description='When student initialize a session. List of tutors receive a notification'
                                'about new session')
        return redirect(reverse('session:profile', kwargs={'pk': request.user.id}))




