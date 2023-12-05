from django import forms

from .models import Link
from .widgets import TagWidget


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ['slug']

        widgets = {
            'tags': TagWidget,
        }

