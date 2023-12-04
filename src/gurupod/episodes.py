from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError
from typing import List, NamedTuple, Set

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser

from gurupod.data.consts import EPISODES_JSON, MAIN_URL


@dataclass
class Episode:
    show_name: str
    show_url: str
    show_notes: list
    show_links: dict
    show_date: datetime.date or str
    num: int = None

    def __post_init__(self):
        if isinstance(self.show_date, str):
            self.show_date = datetime.strptime(self.show_date, "%Y-%m-%d").date()

    def __lt__(self, other):
        return self.show_date < other.show_date

    def __gt__(self, other):
        return self.show_date > other.show_date

    def __eq__(self, other):
        return self.show_date == other.show_date and self.show_name == other.show_name

    def __str__(self):
        return self.show_name

    def __repr__(self):
        return f"Episode({self.__dict__})"

    def __hash__(self):
        return hash(self.show_name + str(self.show_date))

    @property
    def details(self):
        return {k: v for k, v in self.__dict__.items() if k != "show_name"}


class EpTup(NamedTuple):
    name: str
    url: str

    @classmethod
    def from_soup(cls, ep_soup):
        """ ep_soup is a subset of an episodes listing page"""
        return cls(ep_soup.select_one(".episode-title a").text,
                   str(ep_soup.select_one(".episode-title a")['href']))


class EpDetails(NamedTuple):
    notes: list
    links: dict
    date: datetime.date

    @classmethod
    def from_soup(cls, ep_soup):
        """ ep_soup is a complete episode-specific page"""
        return cls(
            notes=ep_soup_notes(ep_soup),
            links=ep_soup_links(ep_soup),
            date=ep_soup_date(ep_soup),
        )


def sort_n_number_eps(eps):
    eps.sort(key=lambda epi: epi.show_date, reverse=True)
    for number, ep in enumerate(reversed(eps), start=1):
        ep.num = number


def all_episodes_():
    existing_dict, existing_eps = existing_episodes_()
    new_eps = asyncio.run(new_episodes_(MAIN_URL, existing_d=existing_dict))
    all_eps = existing_eps + new_eps
    sort_n_number_eps(all_eps)
    if new_eps:
        export_episodes_json(all_eps)
    return all_eps


def existing_episodes_() -> (dict, List[Episode]):
    try:
        with open(EPISODES_JSON, "r") as infile:
            existing_d = json.load(infile)
            existing_eps = [Episode(name, **ep) for name, ep in existing_d.items()]
    except JSONDecodeError:
        print("existing episodes file is empty")
        existing_eps = []
    return existing_d, existing_eps


async def new_episodes_(main_url: str, existing_d: dict or None = None) -> List[Episode]:
    episodes = []
    async with aiohttp.ClientSession() as session:
        pages = await listing_pages_(main_url, session)
        for page in pages:
            eps = await episodes_from_page(page, session, existing_d)
            if not eps:
                break
            episodes.extend(eps)
    return episodes


def export_episodes_json(episodes: List[Episode]):
    with open(EPISODES_JSON, "w") as outfile:
        json.dump({ep.show_name: ep.details for ep in episodes}, outfile, default=str, indent=4,
                  ensure_ascii=True)


async def episodes_from_page(
        page_url: str, session, existing_d: dict or None = None) -> List[Episode]:
    existing_d = existing_d or {}
    new_eps = []

    async for ep_tup in ep_tups_from_url(page_url, session):
        if ep_tup.name in existing_d:
            print(f"Already Exists: {ep_tup.name}")
            return new_eps

        print(f"New episode found: {ep_tup.name}")
        ep_soup = await ep_soup_from_link(ep_tup.url, session)
        ep_details_ = EpDetails.from_soup(ep_soup)
        new_eps.append(Episode(*ep_tup, *ep_details_))

    return new_eps


async def ep_soup_from_link(link, session) -> BeautifulSoup:
    async with session.get(link) as response:
        text = await response.text()
        return BeautifulSoup(text, "html.parser")


##############################


def ep_soup_date(ep_soup) -> datetime.date:
    date_str = ep_soup.select_one(".publish-date").text
    datey = parser.parse(date_str)
    return datey.date()


def ep_soup_notes(soup: BeautifulSoup) -> list:
    ''' some listing have literal("Links") as heading for next section some dont '''

    paragraphs = soup.select(".show-notes p")
    show_notes = [p.text for p in paragraphs if p.text != "Links"]

    return show_notes


def ep_soup_links(soup: BeautifulSoup) -> dict:
    show_links_html = soup.select(".show-notes a")
    show_links_dict = {aref.text: aref['href'] for aref in show_links_html}
    return show_links_dict


###########
async def ep_tups_from_url(page_url: str, session):
    async with session.get(page_url) as response:
        text = await response.text()
    soup = BeautifulSoup(text, "html.parser")
    episodes_soup = soup.select(".episode")
    for ep_soup in episodes_soup:
        yield EpTup.from_soup(ep_soup)
        # yield ep_tup_from_soup(ep_soup)

        # yield (ep_soup.select_one(".episode-title a").text,
        #        str(ep_soup.select_one(".episode-title a")['href']))


async def listing_pages_(main_url: str, session) -> List[str]:
    num_pages = await _get_num_pages(main_url, session)
    return [_url_from_pagenum(main_url, page_num) for page_num in range(num_pages)]


def _url_from_pagenum(main_url: str, page_num: int) -> str:
    return main_url + f"/episodes/{page_num + 1}/#showEpisodes"


async def _get_response(url: str, session):
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


async def _get_num_pages(main_url: str, session) -> int:
    response = await _get_response(main_url, session)
    soup = BeautifulSoup(response, "html.parser")
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.split("/")[-1].split("#")[0]
    return int(num_pages)


##### setty


def all_episodes_set():
    existing_dict, existing_eps = existing_episodes_set()
    new_eps = asyncio.run(
        new_episodes_set(MAIN_URL, existing_d=existing_dict))
    all_eps = existing_eps.union(new_eps)
    if new_eps:
        export_episodes_json(all_eps)
    return all_eps


def existing_episodes_set() -> (dict, Set[Episode]):
    try:
        with open(EPISODES_JSON, "r") as infile:
            existing_d = json.load(infile)
            existing_eps = {Episode(name, **ep) for name, ep in existing_d.items()}
    except JSONDecodeError:
        print("existing episodes file is empty")
        existing_eps = set()
    return existing_d, existing_eps


async def new_episodes_set(main_url: str, existing_d: dict or None = None) -> set[Episode]:
    episodes = set()
    async with aiohttp.ClientSession() as session:
        pages = await listing_pages_(main_url, session)
        for page in pages:
            eps = await episodes_from_page_set(page, session, existing_d)
            if not eps:
                break
            episodes.update(eps)
    return episodes


async def episodes_from_page_set(
        page_url: str, session, existing_d: dict or None = None) -> set[Episode]:
    existing_d = existing_d or {}
    new_eps = set()

    async for ep_tup in ep_tups_from_url(page_url, session):
        if ep_tup.name in existing_d:
            print(f"Already Exists: {ep_tup.name}")
            return new_eps

        print(f"New episode found: {ep_tup.name}")
        ep_soup = await ep_soup_from_link(ep_tup.url, session)
        ep_details_ = EpDetails.from_soup(ep_soup)
        new_eps.add(Episode(*ep_tup, *ep_details_))

    return new_eps
