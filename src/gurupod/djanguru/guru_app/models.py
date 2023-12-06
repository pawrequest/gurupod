from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Guru(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(editable=False, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # return reverse("tag-detail", args=[self.slug])
        return reverse("tag_detail", args=[self.slug])



class Link(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    slug = models.SlugField(editable=False, unique=True)
    narrative = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='link_tags', blank=True)
    gurus = models.ManyToManyField('Guru', related_name='guru_links', blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.url = self.url.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("link_detail", args=[self.slug])



class Episode(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    url = models.URLField()
    notes = models.TextField()
    links = models.ManyToManyField(Link)
    gurus = models.ManyToManyField('Guru', related_name='guru_episodes', blank=True)
    slug = models.SlugField(editable=False, unique=True)


    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse("episode_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.url = self.url.lower()
        super().save(*args, **kwargs)
