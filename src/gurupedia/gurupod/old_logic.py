from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.utils.text import slugify


#
# @dataclass
# class Episode:
#     url: str
#     title: str
#     links: dict # text to url
#     notes: list
#     date: datetime
#
#     def to_dict(self):
#         return {
#             self.title: {
#                 'url': self.url,
#                 'date': self.date.date().isoformat(),
#                 'notes': self.notes,
#                 'links': self.links
#             }
#         }
#
#     @classmethod
#     def from_url(cls, episode_url):
#         """takes a url and returns an Episode object"""
#         response = requests.get(episode_url)
#         soup = BeautifulSoup(response.text, "html.parser")
#
#         return cls(
#             url=episode_url,
#             title=soup.select_one(".episode-title").text,
#             links=show_links_from_soup(soup),
#             notes=show_notes_from_soup(soup),
#             date=parse(soup.select_one(".publish-date").text),
#         )
#
#     @classmethod
#     def many_from_web(cls, main_url):
#         response = requests.get(main_url)
#         mainsoup = BeautifulSoup(response.text, "html.parser")
#         pod_name = mainsoup.select_one(".about-title").text
#         listing_urls = get_listing_urls(mainsoup=mainsoup, main_url=main_url)[:2]  # LIMITED TO 2
#         episode_urls = get_episode_urls(listing_urls=listing_urls)
#
#         return [cls.from_url(episode_url) for episode_url in episode_urls]


def show_notes_from_soup(episode_soup) -> list:
    paragraphs = episode_soup.select(".show-notes p")
    full_show_notes = [p.text for p in paragraphs]
    show_notes = []

    for note in full_show_notes:
        if note == "Links":
            break
        else:
            show_notes.append(note)

    return show_notes


def show_links_from_soup(episode_soup) -> dict:
    show_links_html = episode_soup.select(".show-notes a")
    show_links_dict = {}
    for aref in show_links_html:
        show_links_dict[aref.text] = aref['href']
    return show_links_dict


def show_links_tuple_from_soup(episode_soup) -> list[tuple]:
    show_links_html = episode_soup.select(".show-notes a")
    show_links_tuples = [(aref.text, aref['href']) for aref in show_links_html]
    return show_links_tuples



def get_listing_urls(mainsoup, main_url) -> list[str]:
    page_links = mainsoup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.replace(f"{main_url}/episodes/", "")
    num_pages = int(num_pages.replace("#showEpisodes", ""))  #
    page_urls = []
    for page in range(num_pages):
        # for page in range(1):
        page_urls.append(main_url + f"/episodes/{page + 1}/#showEpisodes")
    return page_urls

def get_episode_urls(listing_urls):
    episode_page_urls = []
    for page in listing_urls:
        response = requests.get(page)
        soup = BeautifulSoup(response.text, "html.parser")
        episode_soup = soup.select(".episode")
        for episode in episode_soup:
            link = episode.select_one(".episode-title a")['href']

            episode_page_urls.append(link)
    return episode_page_urls

    # @classmethod
    # def from_url(cls, url):
    #     response = requests.get(url)
    #     soup = BeautifulSoup(response.text, "html.parser")
    #     return cls(
    #         title=soup.select_one(".episode-title").text,
    #         date=soup.select_one(".publish-date").text,
    #         url=url,
    #         notes=show_notes_from_soup(soup),
    #         links=show_links_from_soup(soup),
    #     )
    #
