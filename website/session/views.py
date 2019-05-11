from django.shortcuts import render, redirect, reverse
from website.access.models import CustomUser, TutorDetails, TutorStatus
from django.views.generic import View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .forms import *


class ProfileDetailsView(LoginRequiredMixin, View):
    template_name = 'website/session/profile.html'
    model = CustomUser, TutorStatus
    login_url = 'access:login'
    redirect_field_name = 'login_required'
    now = timezone.now()

    def get(self, request, *args, **kwargs):
        if request.user.id == kwargs['pk']:
            now = self.now
            form = TutorStatusForm()
            return render(request, self.template_name, locals())
        else:
            return redirect(reverse('session:profile', kwargs={'pk': request.user.id}))

    def post(self, request, *args, **kwargs):
        form = TutorStatusForm(request.POST)
        now = self.now
        if form.is_valid():
            obj, created = TutorStatus.objects.get_or_create(user_id=request.user.id)
            obj.is_active = form.cleaned_data.get('is_active')
            obj.save()
        return render(request, self.template_name, locals())


class TutorDetailsUpdateView(UpdateView):
    model = TutorDetails
    fields = ['dob', 'short_resume', 'phone_number', 'cv']
    template_name = 'website/session/update_tutor_details.html'

    def get_success_url(self):
        return reverse('session:profile', kwargs={'pk': self.object.user_id})


def search_view(request):
    return render(request, template_name='website/session/search.html')
