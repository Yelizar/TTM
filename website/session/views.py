from django.shortcuts import render, reverse, get_object_or_404
from website.access.models import *
from django.views.generic import View, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import *
from django.core.cache import cache
from django.utils.safestring import mark_safe
import json
from django.views.decorators.cache import cache_control, never_cache


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


class TutorDetailsUpdateView(UpdateView):
    model = TutorDetails
    fields = ['languages', 'dob', 'phone_number', 'short_resume', 'cv']
    template_name = 'website/session/update_details.html'

    def get_success_url(self):
        return reverse('session:profile', kwargs={'pk': self.object.user_id})


# class StudentDetailsUpdateView(UpdateView):
#     model = StudentDetails
#     fields = ['languages', 'communication_methods']
#     template_name = 'website/session/update_details.html'
#
#     def get_success_url(self):
#         return reverse('session:profile', kwargs={'pk': self.object.user_id})


class CommunicationMethodNumberCreateView(CreateView):
    template_name = 'website/session/add_com_number.html'
    model = CommunicationMethodNumber
    fields = ['number']

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Temporarily function is limited. Access is allowed only to Appear.in
        form.instance.com_method = CommunicationMethods.objects.get(id=4)
        return super(CommunicationMethodNumberCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('session:profile', kwargs={'pk': self.object.user_id})


class SessionInitialization(View):
    template_name = 'website/session/session_initialization.html'

    @never_cache
    def get(self, request, *args, **kwargs):
        object = CustomUser.objects.get(username=kwargs['session_name'])
        if object != request.user:
            list_tutors = get_object_or_404(ChannelRoom, student_id=object.id, is_active=True)
        session_name_json = mark_safe(json.dumps(kwargs['session_name']))
        return render(request, self.template_name, locals())


