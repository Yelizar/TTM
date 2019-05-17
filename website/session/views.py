from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
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
    fields = ['languages', 'communication_methods',
         'dob', 'phone_number', 'short_resume', 'cv']
    template_name = 'website/session/update_details.html'

    def get_success_url(self):
        return reverse('session:profile', kwargs={'pk': self.object.user_id})


class StudentDetailsUpdateView(UpdateView):
    model = StudentDetails
    fields = ['languages', 'communication_methods']
    template_name = 'website/session/update_details.html'

    def get_success_url(self):
        return reverse('session:profile', kwargs={'pk': self.object.user_id})


def search_view(request):
    return render(request, template_name='website/session/search.html')


class SessionInitialization(View):
    template_name = 'website/session/session_initialization.html'

    def get(self, request, *args, **kwargs):
        student_obj = CustomUser.objects.get(id=request.user.id)
        tutor_obj = CustomUser.objects.get(id=request.session['tutor_pk'])
        if request.is_ajax():
            if request.GET['method']:
                method = request.GET['method']
                data = {}
                try:
                    if student_obj.studentdetails.communication_methods.get(method__contains=method) == tutor_obj.\
                            tutordetails.communication_methods.get(method__contains=method):
                        data['approved_method'] = method
                        request.session['communication_method'] = method
                except CommunicationMethods.DoesNotExist:
                    data['error_message'] = 'Tutor don\'t have ' + method
                return JsonResponse(data)
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            session = Session()
            session.student = CustomUser.objects.get(username=request.POST.get('student'))
            session.tutor = CustomUser.objects.get(username=request.POST.get('tutor'))
            session.language = Languages.objects.get(language=request.POST.get('language'))
            session.communication_method = CommunicationMethods.objects.get(method=request.POST.get('communication_method'))
            session.save()
            meta = {"Session": "Session"}
            return JsonResponse(meta)
        return render(request, self.template_name, locals())

