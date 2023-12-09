from __future__ import annotations

import asyncio
import json
from datetime import datetime
from json import JSONDecodeError
from typing import List, NamedTuple, Set

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser

from data.consts import EPISODES_JSON, MAIN_URL






async def ep_soup_from_link(link, session) -> BeautifulSoup:
    async with session.get(link) as response:
        text = await response.text()
        return BeautifulSoup(text, "html.parser")


##############################


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
    return all_eps


def existing_episodes_set() -> (dict, Set[Episode]):
    try:
        with open(EPISODES_JSON, "r") as infile:
            existing_d = json.load(infile)
            existing_eps = {Episode(name=name, **ep) for name, ep in existing_d.items()}
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

    return new_eps
