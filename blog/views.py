from django.views.generic import DetailView
from .models import Entry


class EntryDetail(DetailView):
    model = Entry
    template_name = 'blog/entry_detail.html'