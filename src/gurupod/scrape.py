from dateutil import parser

import asyncio
from datetime import datetime
from typing import Literal, NamedTuple, TYPE_CHECKING

import aiohttp
import dateutil
from bs4 import BeautifulSoup

from data.consts import MAIN_URL

MAYBE_ATTR = Literal['name', 'notes', 'links', 'date']

if TYPE_CHECKING:
    from gurupod.models.episode import EpisodeIn

    EP_TYP = EpisodeIn
else:
    EP_TYP = dict


def deet_from_soup(deet: MAYBE_ATTR, soup: BeautifulSoup):
    if deet == 'name':
        return soup_title(soup)
    if deet == 'notes':
        return soup_notes(soup)
    if deet == 'links':
        return soup_links(soup)
    if deet == 'date':
        return soup_date(soup)
    else:
        raise ValueError(f'invalid deet: {deet}')


def soup_date(soup) -> datetime:
    date_st = soup.select_one(".publish-date").text
    return parser.parse(date_st)

def soup_notes(soup: BeautifulSoup) -> list:
    """ some listing have literal("Links") as heading for next section some dont """

    paragraphs = soup.select(".show-notes p")
    show_notes = [p.text for p in paragraphs if p.text != "Links"]

    return show_notes or None


def soup_links(soup: BeautifulSoup) -> dict:
    show_links_html = soup.select(".show-notes a")
    show_links_dict = {aref.text: aref['href'] for aref in show_links_html}
    return show_links_dict


def soup_title(soup: BeautifulSoup) -> str:
    return soup.select_one(".episode-title").text


########################


async def parse_main_page(session, main_url=MAIN_URL, existing_eps=None, max_dupes=5) -> list[EP_TYP]:
    existing_eps = existing_eps or []
    listing_pages = await get_lists(main_url, session)
    new_eps = []
    dupes = 0

    for listing_page in listing_pages:
        async for name, url in _get_names_urls(listing_page, session):
            if name in existing_eps:
                if dupes >= max_dupes:
                    print(f"{max_dupes=} stopping")
                    return new_eps
                dupes += 1
                continue
            else:
                ep_page = await _get_response(url, session)
                ep_soup = BeautifulSoup(ep_page, "html.parser")
                new_eps.append(EP_TYP(name=name, url=url, notes=soup_notes(ep_soup),
                                      links=soup_links(ep_soup), date=soup_date(ep_soup)))
    return new_eps


async def get_lists(main_url, session):
    main_html = await _get_response(main_url, session)
    main_soup = BeautifulSoup(main_html, "html.parser")
    num_pages = _get_num_pages(main_soup)
    listing_pages = listing_pages_(main_url, num_pages)
    return listing_pages


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


def listing_pages_(main_url: str, num_pages: int) -> list[str]:
    return [main_url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]


def _get_num_pages(soup: BeautifulSoup) -> int:
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.split("/")[-1].split("#")[0]
    return int(num_pages)


async def _get_names_urls(lisitng_page: str, session):
    text = await _get_response(lisitng_page, session)
    listing_soup = BeautifulSoup(text, "html.parser")
    episodes_soup = listing_soup.select(".episode")
    for ep_soup in episodes_soup:
        yield _EpTup.from_soup(ep_soup)


class _EpTup(NamedTuple):
    name: str
    url: str

    @classmethod
    def from_soup(cls, ep_soup):
        """ ep_soup is a subset of an episodes listing page"""
        return cls(ep_soup.select_one(".episode-title a").text,
                   str(ep_soup.select_one(".episode-title a")['href']))
