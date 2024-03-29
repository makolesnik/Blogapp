from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import render_to_response
import django.http as http 

from .models import Entry, Comment
from tagging.models import Tag, TaggedItem
from .forms import CommentForm


def tags(request):
    return render_to_response('tags.html')

def with_tag(request, tag, object_id=None, page=1):
    query_tag = Tag.objects.get(name=tag)
    entries = TaggedItem.objects.get_by_model(Entry, query_tag)
    entries = entries.order_by('-modified_at')
    return render_to_response('with_tag.html', dict(tag=tag, entries=entries))


class HomeView(ListView):
    template_name = 'index.html'
    queryset = Entry.objects.order_by('-created_at')
    paginate_by = 5

class HomePaginatedView(ListView):
    template_name = 'index.html'
    queryset = Entry.objects.order_by('-created_at')
    paginate_by = 5

class EntryDetail(CreateView):
    model = Entry
    template_name = 'entry_detail.html' 
    form_class = CommentForm
 
    def get_form_kwargs(self):
	kwargs = super(EntryDetail, self).get_form_kwargs()
	kwargs['entry'] = self.get_object()
	return kwargs

    def get_context_data(self, **kwargs):
	d = super(EntryDetail, self).get_context_data(**kwargs)
	d['entry'] = self.get_object()
	return d  

    def get_success_url(self):
	return self.get_object().get_absolute_url() + "#comments"

