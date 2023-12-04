from django.urls import reverse, reverse_lazy
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_select2 import forms as s2forms
from django_select2.forms import ModelSelect2TagWidget, Select2TagWidget

from .models import Tag


class CustomModelSelect2TagWidget(ModelSelect2TagWidget):
    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        attrs.setdefault('data-preview-url', reverse('get_existing_tags'))  # Change 'get_existing_tags' to your view name for fetching existing tags
        return attrs



class Select2OrAddByNameWidget(ModelSelect2TagWidget):

    def value_from_datadict(self, data, files, name):
        '''Create objects for given non-pimary-key values. Return list of all primary keys.'''
        values = set(super().value_from_datadict(data, files, name))
        # This may only work for MyModel, if MyModel has title field.
        # You need to implement this method yourself, to ensure proper object creation.
        pks = self.queryset.filter(name__in=values).values_list('pk', flat=True)
        pks = set(map(str, pks))
        cleaned_values = list(pks)
        for val in values - pks:
            cleaned_values.append(self.queryset.create(name=val).pk)
        return cleaned_values


class TagWidget(Select2OrAddByNameWidget):
    queryset = Tag.objects.all()

    search_fields = [
        "name__icontains",
    ]
#
# class TagWidget(s2forms.ModelSelect2TagWidget):
#     search_fields = [
#         "name__icontains",
#     ]




#
# class RelatedFieldWidgetCanAdd(widgets.Select):
#
#     def __init__(self, related_model, related_url=None, *args, **kw):
#
#         super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kw)
#
#         if not related_url:
#             related_url = f'admin:{related_model._meta.app_label}_{related_model._meta.object_name.lower()}_add'
#
#         # Be careful that here "reverse" is not allowed
#         self.related_url = related_url
#
#     def render(self, name, value, *args, **kwargs):
#         self.related_url = reverse(self.related_url)
#         output = [super(RelatedFieldWidgetCanAdd, self).render(name, value, *args, **kwargs)]
#         output.append(
#             f'<a href="{self.related_url}" class="add-another" id="add_id_{name}" onclick="return showAddAnotherPopup(this);">')
#         output.append(
#             f'<img src="{settings.STATIC_URL}admin/img/icon_addlink.gif" width="10" height="10" alt="Add Another"/></a>')
#         return mark_safe(''.join(output))
#

