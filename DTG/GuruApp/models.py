from django.db import models


class Guru(models.Model):
    name = models.CharField(max_length=200)

class Tag(models.Model):
    name = models.CharField(max_length=50)



class Link(models.Model):
    url = models.URLField()
    description = models.TextField()


class Episode(models.Model):
    show_name = models.CharField(max_length=200)
    show_date = models.DateField()
    show_url = models.URLField()
    show_notes = models.TextField()
    show_links = models.ManyToManyField(Link)
    show_gurus = models.ManyToManyField('Guru', related_name='guru_episodes')
