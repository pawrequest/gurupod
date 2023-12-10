from __future__ import annotations

import asyncio
from datetime import datetime
from enum import Enum
from typing import Generator, List

import sqlmodel
from aiohttp import ClientError, ClientSession as ClientSession
from bs4 import BeautifulSoup
from dateutil import parser
from sqlmodel import select

from data.consts import MAIN_URL
from gurupod.models.episode import Episode, EpisodeDB


## expand episode
class MAYBE_ENUM(Enum):
    name = 'name'
    notes = 'notes'
    links = 'links'
    date = 'date'


async def maybe_expand_episode(ep: Episode) -> Episode:
    if missing := get_missing(ep):
        print(f'\n{ep.name=} is missing data: {[_.value for _ in missing]}')
        ep = await _expand_episode(ep, missing)
    return ep


def get_missing(ep: Episode) -> list[MAYBE_ENUM]:
    return [_ for _ in MAYBE_ENUM if getattr(ep, _.value) is None]


async def _expand_episode(ep: Episode, missing: List[MAYBE_ENUM]) -> Episode:
    async with ClientSession() as aiosession:
        html = await _get_response(ep.url, aiosession)
        soup = BeautifulSoup(html, "html.parser")
        for attr in missing:
            new_value = deet_from_soup(attr.value, soup)
            print(f'\tScraping "{attr.value}" = {new_value}')
            setattr(ep, attr.value, new_value)
        print('\n')
    return ep


def deet_from_soup(deet: MAYBE_ENUM.value, soup: BeautifulSoup):
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


async def episode_scraper(session: sqlmodel.Session, aiosession: ClientSession,
                          main_url: str = MAIN_URL,
                          max_dupes: int = 5, max_return=None) -> list[Episode]:
    existing_urls = session.exec(select(EpisodeDB.url)).all()
    new_eps, dupes = [], 0
    listing_pages = await listing_pages_(main_url, aiosession)
    coroutines = [_get_episdode_urls(listing_page, aiosession) for listing_page in listing_pages]
    results = await asyncio.gather(*coroutines)
    # urls = [*results]
    urls = [_ for sublist in results for _ in sublist]
    for url in urls:
    # for url in await asyncio.gather(*coroutines):
        if max_return and len(new_eps) >= int(max_return):
            print(f"reached {max_return=}, stopping")
            return new_eps
        else:
            print(f'\tChecking episode {url}')
            if url in existing_urls:
                print(f'\t\tAlready Exists #{dupes}\n')
                if dupes >= max_dupes:
                    print(f"reached {max_dupes=}, stopping")
                    return new_eps
                dupes += 1
                continue
            else:
                new_eps.append(await fetch_new_ep(aiosession, url))
    return new_eps


    #     if max_return and len(new_eps) >= int(max_return):
    #         print(f"reached {max_return=}, stopping")
    #         return new_eps
    #     print(f'Scanning listing page: {listing_page}')
    #     # async for url in _get_episdode_urls(listing_page, aiosession):
    #         print(f'\tChecking episode {url}')
    #         if url in existing_urls:
    #             print(f'\t\tAlready Exists #{dupes}\n')
    #             if dupes >= max_dupes:
    #                 print(f"reached {max_dupes=}, stopping")
    #                 return new_eps
    #             dupes += 1
    #             continue
    #         else:
    #             new_eps.append(await fetch_new_ep(aiosession, url))
    # return new_eps


async def fetch_new_ep(aiosession: ClientSession, url: str):
    ep_page = await _get_response(url, aiosession)
    ep_soup = BeautifulSoup(ep_page, "html.parser")
    name = soup_title(ep_soup)
    print(f"New episode found: {name}\n")
    return Episode(name=name, url=url, notes=soup_notes(ep_soup),
                   links=soup_links(ep_soup), date=soup_date(ep_soup))


async def _get_response(url: str, aiosession: ClientSession):
    for _ in range(3):
        try:
            async with aiosession.get(url) as response:
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


async def listing_pages_(main_url: str, session: ClientSession):
    main_html = await _get_response(main_url, session)
    main_soup = BeautifulSoup(main_html, "html.parser")
    num_pages = _get_num_pages(main_soup)
    listing_pages = listing_page_strs_(main_url, num_pages)
    return listing_pages


def _get_num_pages(soup: BeautifulSoup) -> int:
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.split("/")[-1].split("#")[0]
    return int(num_pages)


async def _get_episdode_urls(listing_page: str, aiosession: ClientSession) \
        -> List[str]:
        # -> Generator[str, None, None]:
    text = await _get_response(listing_page, aiosession)
    listing_soup = BeautifulSoup(text, "html.parser")
    episodes_res = listing_soup.select(".episode")
    return [str(ep_soup.select_one(".episode-title a")['href'])for ep_soup in episodes_res]
    # for ep_soup in episodes_soup:
    #     yield str(ep_soup.select_one(".episode-title a")['href'])
