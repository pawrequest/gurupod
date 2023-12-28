""" Scrape website for new episodes """

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator

from aiohttp import ClientError, ClientSession as ClientSession
from bs4 import BeautifulSoup, Tag

from data.consts import DEBUG
from gurupod.gurulog import get_logger
from gurupod.models.episode import EpisodeBase

logger = get_logger()


class MainSoup(BeautifulSoup):
    def __init__(self, markup: str, main_url, parser: str = "html.parser"):
        super().__init__(markup, parser)
        self.main_url = main_url
        self.listing_pages = list()

    @classmethod
    async def from_url(cls, url: str, aiosession: ClientSession):
        html = await _response(url, aiosession)
        main_soup = cls(html, url)
        num_pgs = main_soup._num_pages
        main_soup.listing_pages = _listing_page_strs(url, num_pgs)
        return main_soup

    @property
    def _num_pages(self) -> int:
        page_links = self.select(".page-link")
        lastpage = page_links[-1]["href"]
        num_pages = lastpage.split("/")[-1].split("#")[0]
        return int(num_pages)

    async def listing_soups(self, aiosession) -> AsyncGenerator[ListingSoup, None]:
        for listing_page in self.listing_pages:
            logger.debug(f"Scraping listing page {listing_page}")
            listing_page_soup = await ListingSoup.from_url(listing_page, aiosession)
            yield listing_page_soup

    async def episode_stream(self, aiosession) -> AsyncGenerator[EpisodeBase, None]:
        async for listing_soup in self.listing_soups(aiosession):
            async for ep in listing_soup.episodes():
                yield ep


class ListingSoup(BeautifulSoup):
    def __init__(self, markup: str, lp_url, parser: str = "html.parser"):
        super().__init__(markup, parser)
        self.episode_sections = self.select(".episode")
        self.episode_soups = [ListingEpisodeSubSoup(_) for _ in self.episode_sections]
        self.listing_eps = list()
        self.listing_page_url = lp_url

    async def episodes(self) -> AsyncGenerator[EpisodeBase, None]:
        for ep_subsoup in self.episode_soups:
            ep_detail_soup = await EpisodeDetailsSoup.from_url(ep_subsoup.url)
            list_ep_dict = dict(
                title=ep_subsoup.title,
                url=ep_subsoup.url,
                episode_number=ep_subsoup.episode_number,
                date=ep_subsoup.date,
                notes=ep_detail_soup.episode_notes,
                links=ep_detail_soup.episode_links,
            )
            yield EpisodeBase(**list_ep_dict)

    @classmethod
    async def from_url(cls, url: str, aiosession: ClientSession):
        html = await _response(url, aiosession)
        return cls(html, url)


@dataclass
class ListingEpisodeSubSoup:
    _soup_section: Tag

    @property
    def episode_number(self):
        """string bercause 'bonus' episodes are not numbered"""
        res = self._soup_section.select_one(".episode-info").text.strip().split()[1]
        return res

    @property
    def date(self):
        return self._soup_section.select_one(".publish-date").text.strip()

    @property
    def url(self):
        return self._soup_section.select_one(".episode-title a")["href"]

    @property
    def title(self):
        return self._soup_section.select_one(".episode-title").text.strip()


class EpisodeDetailsSoup(BeautifulSoup):
    def __init__(self, markup: str, parser: str = "html.parser", url=None):
        super().__init__(markup, parser)
        self.episode_url = url

    @property
    def episode_notes(self):
        paragraphs = self.select(".show-notes p")
        show_notes = [p.text for p in paragraphs if p.text != "Links"]

        return show_notes or None

    @property
    def episode_links(self):
        show_links_html = self.select(".show-notes a")
        show_links_dict = {aref.text: aref["href"] for aref in show_links_html}
        return show_links_dict

    @classmethod
    async def from_url(cls, url: str, aiosession: ClientSession = None) -> EpisodeDetailsSoup:
        aiosession = aiosession or ClientSession()
        async with aiosession:
            html = await _response(url, aiosession)
            soup = EpisodeDetailsSoup(html, "html.parser", url=url)
            return soup


async def _response(url: str, aiosession: ClientSession):
    for _ in range(3):
        try:
            async with aiosession.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except ClientError as e:
            logger.error(f"Request failed: {e}")
            await asyncio.sleep(2)
            continue
    else:
        raise ClientError("Request failed 3 times")


def _listing_page_strs(main_url: str, num_pages: int) -> list[str]:
    return [main_url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]
