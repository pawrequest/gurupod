



#
#
# class EpisodeFetcher:
#     def __init__(self, main_url):
#         self.main_url = main_url
#         self.episode_dict = self.get_episode_dict()
#         self.listing_pages = self.get_listing_pages()
#         self.episode_pages = self.get_episode_pages()
#
#     def get_listing_pages(self):
#         return [self.url_from_pagenum(page_num) for page_num in
#                 range(_get_num_pages(self.main_url))]
#
#     def get_episode_pages(self):
#         ...
#
#     def get_episode_dict(self):
#         ep_dict = {}
#         for page in self.listing_pages:
#             new_eps: dict = episodes_from_listing_page(page)
#
#             if new_eps:
#                 print("merging new episodes")
#                 ep_dict.update(new_eps)
#                 continue
#
#             else:
#                 print("no new episodes")
#                 break
#         return ep_dict
#
#     def get_episode_objects(self, ep_dict: dict or None = None) -> List[Episode]:
#         ep_dict = ep_dict or self.episode_dict
#         episode_objects = []
#         for episode_name, details in ep_dict.items():
#             episode_objects.append(Episode(episode_name, **details))
#         return episode_objects
#
#     def url_from_pagenum(self, page_num):
#         page_url = self.main_url + f"/episodes/{page_num + 1}/#showEpisodes"
#         return page_url
