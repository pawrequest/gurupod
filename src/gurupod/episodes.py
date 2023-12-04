from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError
from typing import List

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser

from gurupod.data.consts import EPISODES_JSON, MAIN_URL


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


async def names_n_links_as(page_url: str, session):
    async with session.get(page_url) as response:
        text = await response.text()
    soup = BeautifulSoup(text, "html.parser")
    episode_soup = soup.select(".episode")
    for episode in episode_soup:
        yield (episode.select_one(".episode-title a").text,
               str(episode.select_one(".episode-title a")['href']))


@dataclass
class Episode:
    show_name: str
    show_links: dict
    show_notes: list
    show_date: datetime.date
    show_url: str

    @property
    def details(self):
        return {
            "show_links": self.show_links,
            "show_notes": self.show_notes,
            "show_date": self.show_date,
            "show_url": self.show_url,
        }

    @classmethod
    def from_tup_n_soup(cls, ep_tup, ep_soup) -> Episode:
        return cls(
            show_name=ep_tup[0],
            show_url=ep_tup[1],
            show_date=ep_soup_date(ep_soup),
            show_notes=ep_soup_notes(ep_soup),
            show_links=ep_soup_links(ep_soup),
        )


async def episodes_from_page_as(
        page_url: str, session, existing_eps: dict or None = None) -> List[Episode]:
    existing_eps = existing_eps or {}
    new_eps = []
    async for tup in names_n_links_as(page_url, session):
        if tup[0] in existing_eps:
            print(f"Already Exists: {tup[0]}")
            return new_eps

        print(f"New episode found: {tup[0]}")
        ep_soup = await ep_soup_from_link_as(tup[1], session)
        new_eps.append(Episode.from_tup_n_soup(tup, ep_soup))

    return new_eps


async def ep_soup_from_link_as(link, session) -> BeautifulSoup:
    async with session.get(link) as response:
        text = await response.text()
        return BeautifulSoup(text, "html.parser")


async def get_new_eps_as(main_url: str, existing_eps: dict or None = None) -> List[Episode]:
    episodes = []
    async with aiohttp.ClientSession() as session:
        pages = await get_listing_pages_as(main_url, session)
        for page in pages:
            eps = await episodes_from_page_as(page, session, existing_eps)
            if not eps:
                break
            episodes.extend(eps)
    return episodes


async def get_listing_pages_as(main_url: str, session) -> List[str]:
    num_pages = await _get_num_pages_as(main_url, session)
    return [_url_from_pagenum_as(main_url, page_num) for page_num in range(num_pages)]


def _url_from_pagenum_as(main_url: str, page_num: int) -> str:
    return main_url + f"/episodes/{page_num + 1}/#showEpisodes"


async def _get_response_as(url: str, session):
    for _ in range(3):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            print(f"Request failed: {e}")
            await asyncio.sleep(2)
            continue
    else:
        raise aiohttp.ClientError("Request failed 3 times")


async def _get_num_pages_as(main_url: str, session) -> int:
    response = await _get_response_as(main_url, session)
    soup = BeautifulSoup(response, "html.parser")
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.split("/")[-1].split("#")[0]
    return int(num_pages)


def get_eps():
    existing_dict, existing_eps = existing_eps_()
    new_eps = asyncio.run(get_new_eps_as(MAIN_URL, existing_eps=existing_dict))
    all_eps = existing_eps + new_eps
    if new_eps:
        eps_to_json_(all_eps)
    return all_eps


def existing_eps_() -> (dict, List[Episode]):
    try:
        with open(EPISODES_JSON, "r") as infile:
            existing = json.load(infile)
            existing_eps = [Episode(name, **ep) for name, ep in existing.items()]
    except JSONDecodeError:
        print("existing episodes file is empty")
        existing_eps = []
    return existing, existing_eps


def eps_to_json_(all_eps):
    with open(EPISODES_JSON, "w") as outfile:
        json.dump({ep.show_name: ep.details for ep in all_eps}, outfile, default=str, indent=4,
                  ensure_ascii=True)
