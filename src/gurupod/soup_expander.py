from __future__ import annotations

import asyncio
from typing import Sequence

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from dateutil import parser

from gurupod.gurulog import get_logger, log_episodes
from gurupod.models.episode import EpisodeBase
from gurupod.scrape import _response

logger = get_logger()


async def expand_and_sort(episodes: Sequence[EpisodeBase]) -> list[EpisodeBase]:
    logger.info(f"Expanding {len(episodes)} episodes")
    complete: list[EpisodeBase] = [_ for _ in episodes if not _.data_missing]

    if missing := [_ for _ in episodes if _.data_missing]:
        # log_episodes(missing, msg="Expanding episodes:")
        coroutines = [expand_episode(_) for _ in missing]
        expanded = await asyncio.gather(*coroutines)
        complete.extend(expanded)
    # log_episodes(complete, msg="Complete episodes:")
    return sorted(complete, key=lambda x: x.date)


async def expand_episode(ep: EpisodeBase) -> EpisodeBase:
    soup = await EpisodeSoup.from_url(ep.url)
    epdict = soup.get_ep_d()
    res = EpisodeBase(**epdict, title=ep.title)
    return res


# async def expand_episodeold(url_or_ep: str | EpisodeBase) -> EpisodeBase:
#     if isinstance(url_or_ep, EpisodeBase):
#         url = url_or_ep.url
#     else:
#         url = url_or_ep
#
#     soup = await EpisodeSoup.from_url(url)
#     res = EpisodeBase(**soup.get_ep_d())
#     res.url = url
#     return res


class EpisodeSoup(BeautifulSoup):
    def __init__(self, markup: str, parser: str = "html.parser", url=None):
        super().__init__(markup, parser)
        self.episode_url = url

    # no don't do this because they released a new episode overwriting old url so we get title from listing page to preserve old data
    # @property
    # def episode_title(self):
    #     return self.select_one(".episode-title").text

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

    @property
    def episode_date(self):
        date_st = self.select_one(".publish-date").text
        return parser.parse(date_st)

    def get_ep_d(self):
        return dict(
            url=self.episode_url,
            notes=self.episode_notes,
            links=self.episode_links,
            date=self.episode_date,
        )

    @classmethod
    async def from_url(cls, url: str, aiosession: ClientSession = None) -> EpisodeSoup:
        aiosession = aiosession or ClientSession()
        async with aiosession:
            html = await _response(url, aiosession)
            soup = EpisodeSoup(html, "html.parser", url=url)
            return soup
