from django.shortcuts import render, redirect, get_object_or_404
from .forms import EpisodeForm
from .models import Episode, Tag

def add_content(request):
    if request.method == 'POST':
        form = EpisodeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('content_list')
    else:
        form = EpisodeForm()
    return render(request, 'GuruApp/add_episode.html', {'form': form})


def list_episodes(request, tag_id=None):
    if tag_id:
        tag = get_object_or_404(Tag, pk=tag_id)
        episode = Episode.objects.filter(tags=tag)
    else:
        episode = Episode.objects.all()
    return render(request, 'myapp/content_list.html', {'episode': episode})


