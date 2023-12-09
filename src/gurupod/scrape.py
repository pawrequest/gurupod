from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Generator, Literal, NamedTuple, TYPE_CHECKING

from aiohttp import ClientError, ClientSession as AioSession
from bs4 import BeautifulSoup, Tag
from dateutil import parser

from data.consts import MAIN_URL

MAYBE_ATTR = Literal['name', 'notes', 'links', 'date']

if TYPE_CHECKING:
    from gurupod.models.episode import Episode

    EPISODE_TYPE = Episode
else:
    EPISODE_TYPE = dict


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


def soup_date(soup: BeautifulSoup) -> datetime:
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


async def scrape_new_eps_url(aiosession: AioSession, main_url: str = MAIN_URL,
                             existing_urls: set or None = None,
                             max_dupes: int = 5) -> list[EPISODE_TYPE]:
    if not existing_urls:
        print('no existing episodes provided, fetching all episodes')
        existing_urls = set()
    new_eps = []
    dupes = 0

    for listing_page in await listing_pages_(main_url, aiosession):
        async for url in _get_episdode_urls(listing_page, aiosession):
            if url in existing_urls:
                print(f'Already Exists: {url}')
                if dupes >= max_dupes:
                    print(f"{max_dupes=} stopping")
                    return new_eps
                dupes += 1
                continue
            else:
                new_eps.append(await fetch_new_ep(aiosession, url))
    return new_eps


async def fetch_new_ep(aiosession: AioSession, url: str):
    ep_page = await _get_response(url, aiosession)
    ep_soup = BeautifulSoup(ep_page, "html.parser")
    name = soup_title(ep_soup)
    print(f"New episode found: {name}")
    return EPISODE_TYPE(name=name, url=url, notes=soup_notes(ep_soup),
                        links=soup_links(ep_soup), date=soup_date(ep_soup))


async def listing_pages_(main_url: str, session: AioSession):
    main_html = await _get_response(main_url, session)
    main_soup = BeautifulSoup(main_html, "html.parser")
    num_pages = _get_num_pages(main_soup)
    listing_pages = listing_page_strs_(main_url, num_pages)
    return listing_pages


async def _get_response(url: str, session: AioSession):
    for _ in range(3):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except ClientError as e:
            print(f"Request failed: {e}")
            await asyncio.sleep(2)
            continue
    else:
        raise ClientError("Request failed 3 times")


def listing_page_strs_(main_url: str, num_pages: int) -> list[str]:
    return [main_url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]


def _get_num_pages(soup: BeautifulSoup) -> int:
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.split("/")[-1].split("#")[0]
    return int(num_pages)


async def _get_episdode_urls(lisitng_page: str, aiosession: AioSession) -> Generator[
    str, None, None]:
    text = await _get_response(lisitng_page, aiosession)
    listing_soup = BeautifulSoup(text, "html.parser")
    episodes_soup = listing_soup.select(".episode")
    for ep_soup in episodes_soup:
        yield str(ep_soup.select_one(".episode-title a")['href'])



