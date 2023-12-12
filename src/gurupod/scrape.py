""" Scrape website for new episodes """

from __future__ import annotations

import asyncio
from asyncio import create_task
from typing import List

import sqlmodel
from aiohttp import ClientError, ClientSession as ClientSession
from bs4 import BeautifulSoup
from sqlmodel import select

from data.consts import MAIN_URL
from gurupod.disptaching import _worker
from gurupod.models.episode import Episode, EpisodeDB




async def episode_scraper(session: sqlmodel.Session, aiosession: ClientSession,
                          main_url: str = MAIN_URL,
                          max_dupes: int = 5, max_return=None) -> list[Episode]:
    existing_urls = session.exec(select(EpisodeDB.url)).all()
    new_eps, dupes = [], 0
    listing_pages = await listing_pages_(main_url, aiosession)
    coroutines = [_get_episdode_urls(listing_page, aiosession) for listing_page in listing_pages]
    results = await asyncio.gather(*coroutines)
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
                new_eps.append(
                    Episode(url=url)
                )
    return new_eps


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


async def listing_pages_(main_url: str, session: ClientSession):
    main_html = await _get_response(main_url, session)
    main_soup = BeautifulSoup(main_html, "html.parser")
    num_pages = _get_num_pages(main_soup)
    listing_pages = listing_page_strs_(main_url, num_pages)
    return listing_pages


def listing_page_strs_(main_url: str, num_pages: int) -> list[str]:
    return [main_url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]


def _get_num_pages(soup: BeautifulSoup) -> int:
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.split("/")[-1].split("#")[0]
    return int(num_pages)


async def _get_episdode_urls(listing_page: str, aio_session: ClientSession) \
        -> List[str]:
    # -> Generator[str, None, None]:
    text = await _get_response(listing_page, aio_session)
    listing_soup = BeautifulSoup(text, "html.parser")
    episodes_res = listing_soup.select(".episode")
    return [str(ep_soup.select_one(".episode-title a")['href']) for ep_soup in episodes_res]
    # for ep_soup in episodes_soup:
    #     yield str(ep_soup.select_one(".episode-title a")['href'])


