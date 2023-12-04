from __future__ import annotations, annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from dateutil import parser


@dataclass
class Episode:
    show_name: str
    show_links: dict
    show_notes: list
    show_date: datetime.date
    show_url: str

    @classmethod
    def from_tup_n_soup(cls, ep_tup, ep_soup) -> Episode:
        return cls(
            show_name=ep_tup[0],
            show_url=ep_tup[1],
            show_date=ep_soup_date(ep_soup),
            show_notes=ep_soup_notes(ep_soup),
            show_links=ep_soup_links(ep_soup),
        )


def get_all_episodes(main_url: str, existing_eps: dict or None = None) -> List[Episode]:
    episodes = []
    for page in get_listing_pages(main_url):
        eps = episodes_from_listing_page(page, existing_eps)
        if not eps:
            break
        episodes.extend(eps)
    return episodes


def episodes_from_listing_page(page_url: str, existing_eps: dict or None = None) -> List[Episode]:
    existing_eps = existing_eps or {}
    new_eps = []
    ep_tups = list_page_names_links(page_url)
    for tup in ep_tups:
        if tup[0] in existing_eps:
            print(f"Already Exists: {tup[0]}")
            return new_eps

        print(f"New episode found: {tup[0]}")
        ep_soup = ep_soup_from_link(tup[1])
        new_eps.append(Episode.from_tup_n_soup(tup, ep_soup))

    #
    # for title, link in ep_tups:
    #     if title in existing_eps:
    #         print(f"Already Exists: {title}")
    #         return new_eps
    #
    #     print(f"New episode found: {title}")
    #     ep_soup = ep_soup_from_link(link)
    #     new
    #     new_eps.append(Episode(
    #         show_name=title,
    #         show_url=link,
    #         show_date=ep_soup_date(ep_soup),
    #         show_notes=ep_soup_notes(ep_soup),
    #         show_links=ep_soup_links(ep_soup),
    #     ))

    return new_eps


def _get_response(url: str):
    for _ in range(3):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(2)
            continue
    else:
        raise requests.exceptions.RequestException("Request failed 3 times")


def _get_num_pages(main_url: str) -> int:
    """
    gets number of pages from the 'last' button on captivate.fm
    :param main_url:
    :return num_pages:
    """
    response = _get_response(main_url)
    soup = BeautifulSoup(response.text, "html.parser")
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.replace("https://decoding-the-gurus.captivate.fm/episodes/", "")
    num_pages = int(num_pages.replace("#showEpisodes", ""))  #

    return num_pages


def get_listing_pages(main_url: str) -> List[str]:
    return [_url_from_pagenum(main_url, page_num) for page_num in range(_get_num_pages(main_url))]


def _url_from_pagenum(main_url: str, page_num: int) -> str:
    page_url = main_url + f"/episodes/{page_num + 1}/#showEpisodes"
    return page_url


# Soupy functions:


def list_page_names_links(page_url: str) -> tuple[tuple[str, str]]:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    episode_soup = soup.select(".episode")
    episodes = ((episode.select_one(".episode-title a").text,
                 str(episode.select_one(".episode-title a")['href'])) for episode in episode_soup)

    return tuple(episodes)


def ep_soup_from_link(link) -> BeautifulSoup:
    response = _get_response(link)
    return BeautifulSoup(response.text, "html.parser")


def ep_soup_date(ep_soup) -> datetime.date:
    date_str = ep_soup.select_one(".publish-date").text
    datey = parser.parse(date_str)
    return datey.date()


def ep_soup_notes(soup: BeautifulSoup) -> list:
    ''' some listing have literal("Links") some dont '''

    paragraphs = soup.select(".show-notes p")
    show_notes = [p.text for p in paragraphs if p.text != "Links"]

    return show_notes


def ep_soup_links(soup: BeautifulSoup) -> dict:
    show_links_html = soup.select(".show-notes a")
    show_links_dict = {aref.text: aref['href'] for aref in show_links_html}
    return show_links_dict
