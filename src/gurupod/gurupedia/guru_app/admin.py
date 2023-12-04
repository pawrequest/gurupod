from django.contrib import admin

from .models import Episode, Guru, Link, Tag

# Register your models here.
admin.site.register(Tag)
admin.site.register(Guru)
admin.site.register(Link)
admin.site.register(Episode)
