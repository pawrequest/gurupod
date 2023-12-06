from django.urls import path

from .api import AllEpisodeUrls, AllEpisodes
from .views import LinkCreateView, LinkListView, TagListView, link_detail, tag_detail

urlpatterns = [
    path('links/', LinkListView.as_view(), name='link-add'),
    path('links/add/', LinkCreateView.as_view(), name='link-add'),
    path('links/<slug:slug>', link_detail, name='link_detail'),

    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<slug:slug>/', tag_detail, name='tag_detail'),

    # path('episode-from-url/', EpisodeImporter.as_view(), name='episode_from_url'),
    path('all-episodes/', AllEpisodes.as_view(), name='all_episodes'),
    path('all-episode-urls/', AllEpisodeUrls.as_view(), name='all_episodes_urls'),
    # path('bulk-importer/', BulkImporterAPI.as_view(), name='all_episodes_urls'),

]
