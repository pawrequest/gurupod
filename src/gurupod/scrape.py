""" Scrape website for new episodes """

from __future__ import annotations

import asyncio

from aiohttp import ClientError, ClientSession as ClientSession
from bs4 import BeautifulSoup


async def scrape_urls(aiosession, main_url, max_rtn=None) -> list[str]:
    listing_pages = await _listing_pages(main_url, aiosession)
    tasks = [asyncio.create_task(_episode_urls_from_listing(_, aiosession)) for _ in listing_pages]
    result = await asyncio.gather(*tasks)
    urls = [url for sublist in result for url in sublist]
    if max_rtn is None:
        max_rtn = len(urls)
    return urls[:max_rtn]


async def _episode_urls_from_listing(listing_page: str, aio_session: ClientSession) -> list[str]:
    text = await _response(listing_page, aio_session)
    listing_soup = BeautifulSoup(text, "html.parser")
    episodes_res = listing_soup.select(".episode")
    urls = [str(ep_soup.select_one(".episode-title a")['href']) for ep_soup in episodes_res]
    return urls


async def _response(url: str, aiosession: ClientSession):
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


async def _listing_pages(main_url: str, session: ClientSession) -> list[str]:
    main_html = await _response(main_url, session)
    main_soup = BeautifulSoup(main_html, "html.parser")
    num_pages = _num_pages(main_soup)
    listing_pages = _listing_page_strs(main_url, num_pages)
    return listing_pages


def _listing_page_strs(main_url: str, num_pages: int) -> list[str]:
    return [main_url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]


def _num_pages(soup: BeautifulSoup) -> int:
    page_links = soup.select(".page-link")
    lastpage = page_links[-1]['href']
    num_pages = lastpage.split("/")[-1].split("#")[0]
    return int(num_pages)
