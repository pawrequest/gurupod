import asyncio
from typing import List

import aiohttp
from bs4 import BeautifulSoup

from data.consts import MAIN_URL
from data.dld import EXISTING_EPS
from gurupod.episode import Episode, get_listing_pages, names_n_links


async def get_all_eps_as(main_url: str, existing_eps: dict or None = None) -> List[Episode]:
    episodes = []
    async with aiohttp.ClientSession() as session:
        for page in get_listing_pages(main_url):
            eps = await episodes_from_page_as(page, session, existing_eps)
            if not eps:
                break
            episodes.extend(eps)
    return episodes


async def episodes_from_page_as(page_url: str, session, existing_eps: dict or None = None) -> \
        List[Episode]:
    existing_eps = existing_eps or {}
    new_eps = []
    ep_tups = names_n_links(page_url)
    for tup in ep_tups:
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


eps = asyncio.run(get_all_eps_as(MAIN_URL, existing_eps=EXISTING_EPS))
...
