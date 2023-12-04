from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from .forms import LinkForm
from .models import Link, Tag


# def list_episodes(request, tag_id=None):
#     if tag_id:
#         tag = get_object_or_404(Tag, pk=tag_id)
#         episode = Episode.objects.filter(tags=tag)
#     else:
#         episode = Episode.objects.all()
#     return render(request, 'list_episodes.html', {'episode': episode})
#

class LinkCreateView(CreateView):
    model = Link
    form_class = LinkForm
    # fields = ['url', 'description', 'tags']


class LinkListView(ListView):
    model = Link
    fields = ['url', 'description', 'tags']


# class TagCreateView(CreateView):
#     model = Tag
#     fields = ['name']
#     widgets = {
#         'name': TagWidget,
#     }
#     success_url = reverse_lazy('tag-list')

class TagListView(ListView):
    model = Tag
    fields = ['name']


def link_detail(request, slug):
    link = get_object_or_404(Link, slug=slug)
    return render(request, 'gurupod/link_detail.html', {'link': link, })


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    # You can use the 'tag' object to retrieve the details of the specific tag
    return render(request, 'gurupod/tag_detail.html', {'tag': tag})


# class BookCreateView(CreateView):
#     model = Book
#     form_class = BookForm
#     success_url = "/"

def get_existing_tags(request):
    tags = Tag.objects.values_list('name', flat=True)
    return JsonResponse(list(tags), safe=False)
