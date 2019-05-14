from django.shortcuts import render, redirect, reverse
from website.access.models import *
from django.views.generic import View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone


class ProfileDetailsView(LoginRequiredMixin, View):
    template_name = 'website/session/profile.html'
    login_url = 'access:login'
    redirect_field_name = 'login_required'
    now = timezone.now()

    def get(self, request, *args, **kwargs):
        object = CustomUser.objects.get(id=kwargs['pk'])
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
    fields = ['dob', 'short_resume', 'phone_number', 'cv']
    template_name = 'website/session/update_details.html'

    def get_success_url(self):
        return reverse('session:profile', kwargs={'pk': self.object.user_id})


class StudentDetailsUpdateView(UpdateView):
    model = StudentDetails
    fields = ['dob', 'short_resume', 'phone_number', 'cv']
    template_name = 'website/session/update_details.html'

    def get_success_url(self):
        return reverse('session:profile', kwargs={'pk': self.object.user_id})


def search_view(request):
    return render(request, template_name='website/session/search.html')
