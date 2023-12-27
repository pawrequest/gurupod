""" Scrape website for new episodes """

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Optional

from aiohttp import ClientError, ClientSession as ClientSession
from bs4 import BeautifulSoup, Tag
from sqlmodel import Field

from data.consts import MAIN_URL
from gurupod.gurulog import get_logger
from gurupod.database import SQLModel

logger = get_logger()


async def do_stuff():
    async with ClientSession() as aiosession:
        mainsoup = await MainSoup.from_url(MAIN_URL, aiosession)
        async for listing_page_soup in mainsoup.gen_listing_soups(aiosession):
            async for listing_ep in listing_page_soup.gen_l_eps():
                print(listing_ep.title)
            ...


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

    async def gen_listing_soups(self, aiosession) -> AsyncGenerator[ListingPageSoup, None]:
        for listing_page in self.listing_pages:
            logger.debug(f"Scraping listing page {listing_page}")
            listing_page_soup = await ListingPageSoup.from_url(listing_page, aiosession)
            yield listing_page_soup


class ListingEpisodeBase(SQLModel):
    title: str
    url: str
    episode_number: int
    date: str


class ListingEpisode(ListingEpisodeBase, table=True):
    id: int = Field(default=None, primary_key=True)
    episode_id: Optional[int] = Field(default=None, foreign_key="Episode.id")


class ListingPageSoup(BeautifulSoup):
    def __init__(self, markup: str, parser: str = "html.parser"):
        super().__init__(markup, parser)
        self.episode_sections = self.select(".episode")
        self.episode_soups = [EpisodeSoupSection(_) for _ in self.episode_sections]
        self.listing_eps = list()

    async def gen_l_eps(self) -> AsyncGenerator[ListingEpisode, None]:
        for ep_section_soup in self.episode_soups:
            list_ep = ListingEpisode(
                title=ep_section_soup.title,
                url=ep_section_soup.url,
                episode_number=ep_section_soup.episode_number,
                date=ep_section_soup.date,
            )
            yield list_ep

    @classmethod
    async def from_url(cls, url: str, aiosession: ClientSession):
        html = await _response(url, aiosession)
        return cls(html)


@dataclass
class EpisodeSoupSection:
    soup_section: Tag

    @property
    def episode_number(self):
        res = self.soup_section.select_one(".episode-info").text.strip().split()[1]
        return int(res)

    @property
    def date(self):
        return self.soup_section.select_one(".publish-date").text.strip()

    @property
    def url(self):
        return self.soup_section.select_one(".episode-title a")["href"]

    @property
    def title(self):
        return self.soup_section.select_one(".episode-title").text.strip()


#
# async def scrape_titles_urls(aiosession: ClientSession, main_url) -> AsyncGenerator[tuple[str, str], None]:
#     listing_pages = await _listing_pages(main_url, aiosession)
#     new = []
#     for i, _ in enumerate(listing_pages):
#         if DEBUG:
#             logger.debug(f"Scraping page {i + 1} of {len(listing_pages)}")
#         async for title, url in _episode_titles_and_urls_from_listing(_, aiosession):
#             yield title, url
#
#
# async def title_from_soup_section(soup_section):
#     return soup_section.select_one(".episode-title").text.strip()
#
#
# async def url_from_soup_section(soup_section):
#     return soup_section.select_one(".episode-title a")["href"]
#
#
# def date_from_soup_section(soup_section):
#     return soup_section.select_one(".publish-date").text.strip()
#
#
# async def ep_number_from_soup_section(soup_section):
#     return soup_section.select_one(".episode-info").text.strip()


# async def _episode_titles_and_urls_from_listing(
#     listing_page: str, aio_session: ClientSession
# ) -> AsyncGenerator[tuple[str, str], None]:
#     text = await _response(listing_page, aio_session)
#     listing_soup = BeautifulSoup(text, "html.parser")
#     episodes_res = listing_soup.select(".episode")
#     for soup_section in episodes_res:
#         title = title_from_soup_section(soup_section)
#         url = url_from_soup_section(soup_section)
#         yield title, url


# async def _episode_titles_and_urls_from_listingold(
#     listing_page: str, aio_session: ClientSession
# ) -> tuple[tuple[str, str], ...]:
#     text = await _response(listing_page, aio_session)
#     listing_soup = BeautifulSoup(text, "html.parser")
#     episodes_res = listing_soup.select(".episode")
#     output = []
#     for soup_section in episodes_res:
#         title = soup_section.select_one(".episode-title").text
#         url = soup_section.select_one(".episode-title a")["href"]
#         output.append((title, url))
#     return tuple(output)


# async def _episode_urls_from_listing(listing_page: str, aio_session: ClientSession) -> list[str]:
#     text = await _response(listing_page, aio_session)
#     listing_soup = BeautifulSoup(text, "html.parser")
#     episodes_res = listing_soup.select(".episode")
#     urls = [str(ep_soup.select_one(".episode-title a")["href"]) for ep_soup in episodes_res]
#     return urls


# async def _listing_pages(main_url: str, session: ClientSession) -> list[str]:
#     main_html = await _response(main_url, session)
#     main_soup = BeautifulSoup(main_html, "html.parser")
#     num_pages = _num_pages(main_soup)
#     listing_pages = _listing_page_strs(main_url, num_pages)
#     return sorted(listing_pages, key=lambda x: int(x.split("/")[-2]))


# def _num_pages(soup: BeautifulSoup) -> int:
#     page_links = soup.select(".page-link")
#     lastpage = page_links[-1]["href"]
#     num_pages = lastpage.split("/")[-1].split("#")[0]
#     return int(num_pages)


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


if __name__ == "__main__":
    asyncio.run(do_stuff())
