from django.shortcuts import render, redirect, reverse, get_object_or_404
from website.access.models import *
from django.views.generic import View, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import *
from django.core.cache import cache
from django.utils.safestring import mark_safe
import json
from django.views.decorators.cache import cache_control, never_cache
from .forms import SessionCompletionForm


class ProfileDetailsView(LoginRequiredMixin, View):
    template_name = 'website/session/profile.html'
    login_url = 'access:login'
    redirect_field_name = 'login_required'
    now = timezone.now()

    def get(self, request, *args, **kwargs):
        object = CustomUser.objects.get(id=kwargs['pk'])
        if request.user.id != object.id:
            request.session['tutor_pk'] = object.id
        now = self.now
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        object = CustomUser.objects.get(id=kwargs['pk'])
        now = timezone.now()
        if 'tutor_status' in request.POST:
            request.user.tutorstatus.tutor_status()
        return render(request, self.template_name, locals())


class SessionInitialization(View):
    template_name = 'website/session/session_initialization.html'

    @never_cache
    def get(self, request, *args, **kwargs):
        object = CustomUser.objects.get(username=kwargs['session_name'])
        if object != request.user:
            list_tutors = get_object_or_404(ChannelRoom, student_id=object.id, is_active=True)
        session_name_json = mark_safe(json.dumps(kwargs['session_name']))
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


