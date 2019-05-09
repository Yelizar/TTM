from django.shortcuts import render
from website.access.models import CustomUser
from django.views.generic import DetailView
from django.utils import timezone


class ProfileDetailView(DetailView):
    template_name = 'website/session/profile.html'
    model = CustomUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


def search_view(request):
    return render(request, template_name='website/session/search.html')
