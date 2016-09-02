from django.views.generic.base import TemplateView
from django.views.generic import ListView

from blog.models import Entry


class HomeView(TemplateView):

	template_name = 'index.html'

	queryset = Entry.objects.order_by('-created_at')