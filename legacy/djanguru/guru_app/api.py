import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.utils.text import slugify
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from .models import Episode, Link


class EpisodeFromData(APIView):
    def post(self, request, format=None):
        # Retrieve data from the request
        title = request.data.get('title')
        date = request.data.get('date')
        url = request.data.get('url')
        notes = request.data.get('notes')
        links = request.data.get('links')

        # Create a new Episode object
        episode = Episode.objects.create(
            title=title,
            date=date,
            url=url,
            notes=notes
        )

        # Return a response with the new Episode object's ID
        return Response({'id': episode.id}, status=status.HTTP_201_CREATED)


class EpisodeSerializer(ModelSerializer):
    class Meta:
        model = Episode
        fields = ['title', 'date', 'url', 'notes', 'links', 'gurus', 'slug']


class AllEpisodes(APIView):
    def get(self, format=None):
        episodes = Episode.objects.all()
        serializer = EpisodeSerializer(episodes, many=True)
        return Response(serializer.data)


class AllEpisodeUrls(APIView):
    def get(self, format=None):
        episodes = Episode.objects.all().values_list('url', flat=True)
        return Response(episodes)


# class EpisodeImporter(APIView):
#     def post(self, request, format=None):
#         # Retrieve data from the request
#         episode_url = request.data.get('episode_url')
#         print(f'episode importer : {episode_url=}')
#
#         if Episode.objects.filter(url=episode_url).exists():
#             print(f'API ERROR Episode already exists {episode_url}')
#             return Response({'error': 'Episode already exists'}, status=status.HTTP_400_BAD_REQUEST)
#
#         response = requests.get(episode_url)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")
#         links_dict = show_links_from_soup(soup)
#         episode_links = get_or_create_links(links_dict)
#         try:
#             episode = Episode.objects.create(
#                 url=episode_url,
#                 title=soup.select_one(".episode-title").text,
#                 notes=show_notes_from_soup(soup),
#                 date=parse(soup.select_one(".publish-date").text),
#             )
#             episode.links.set(episode_links)
#         except Exception as e:
#             print(e)
#             ...
#         else:
#             print(f'Episode imported : {episode.title} {episode.date}')
#             return Response({'id': episode.id}, status=status.HTTP_201_CREATED)


def get_or_create_links(links: dict) -> list[Link]:
    """takes a dict of links text-to-url, either retrieves or creates Link objects and returns the full list"""
    names = links.keys()
    slugs = [slugify(name) for name in links.keys()]
    urls = [link.lower() for link in links.values()]
    all_slugs = set(Link.objects.all().values_list('slug', flat=True))
    existing_link_names = Link.objects.filter(slug__in=slugs)
    existing_link_urls = Link.objects.filter(url__in=urls)

    existing_slugs = set(existing_link_names.values_list('slug', flat=True))
    existing_urls = set(existing_link_urls.values_list('url', flat=True))

    new_links = []
    for name, slug, link in zip(names, slugs, urls):

        if link in existing_urls:
            print(f'Link already exists {name} {link}')
            continue
        # while slug in all_slugs:
        while Link.objects.filter(slug__exact=slug).exists():
            print(f'Link name slug already exists {name} - renaming to {name}-a')
            name = f'{name}-a'
            slug = slugify(name)
        print(f'creating new link {name} - {link}')
        new_links.append(Link.objects.create(name=name, url=link))

    return list(existing_link_urls) + new_links

# def all_to_add():
#     all_episodes = set(ALL_EPISODE_URLS)
#     print(f'{len(all_episodes)=}')
#     existing = set(Episode.objects.all().values_list('url', flat=True))
#     print(f'{len(existing)=}')
#     return all_episodes - existing

# class BulkImporterAPI(APIView):
#     def post(self, request, format=None):
#         fails = []
#         eps_to_add = all_to_add()
#         for episode_url in eps_to_add:
#             episode_url = episode_url.lower()
#             print(f'episode importer : {episode_url=}')
#
#             if Episode.objects.filter(url=episode_url).exists():
#                 print(f'API ERROR Episode already exists {episode_url}')
#
#             try:
#                 response = requests.get(episode_url)
#                 response.raise_for_status()
#                 soup = BeautifulSoup(response.text, "html.parser")
#                 links_dict = show_links_from_soup(soup)
#                 episode_links = get_or_create_links(links_dict)
#                 episode = Episode.objects.create(
#                     url=episode_url,
#                     title=soup.select_one(".episode-title").text,
#                     notes=show_notes_from_soup(soup),
#                     date=parse(soup.select_one(".publish-date").text),
#                 )
#                 episode.links.set(episode_links)
#                 print(f'Episode imported : {episode.title} {episode.date}')
#             except Exception as e:
#                 fails.append(episode_url)
#                 print(e)
#                 continue
#             else:
#                 return Response({'fails': fails}, status=status.HTTP_201_CREATED)
