from django.shortcuts import render, redirect, reverse
from website.access.models import CustomUser, TutorDetails
from django.views.generic import View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone


class ProfileDetailView(LoginRequiredMixin, View):
    template_name = 'website/session/profile.html'
    model = CustomUser
    login_url = 'access:login'
    redirect_field_name = 'login_required'

    def get(self, request, *args, **kwargs):
        if request.user.id == kwargs['pk']:
            now = timezone.now()
            return render(request, self.template_name, locals())
        else:
            return redirect(reverse('session:profile', kwargs={'pk': request.user.id}))


class TutorDetailsUpdateView(UpdateView):
    model = TutorDetails
    fields = ['dob', 'short_resume', 'phone_number', 'cv']
    template_name = 'website/session/update_tutor_details.html'

    def get_success_url(self):
        print(self.object.user_id)
        return reverse('session:profile', kwargs={'pk': self.object.user_id})


def search_view(request):
    return render(request, template_name='website/session/search.html')
