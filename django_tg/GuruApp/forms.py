from django import forms
from .models import Episode, Tag

class EpisodeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all())
    class Meta:
        model = Episode
        fields = ['show_name', 'show_url', 'show_notes', 'show_links', 'show_gurus']
