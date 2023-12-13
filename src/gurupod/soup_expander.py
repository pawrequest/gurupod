from __future__ import annotations

import asyncio
from typing import Sequence

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from dateutil import parser

from gurupod.models.episode import Episode
from gurupod.scrape import _response


async def expand_and_sort(episodes: Sequence[Episode]) -> list[Episode]:
    complete: list[Episode] = [_ for _ in episodes if not _.data_missing]

    if missing := [_ for _ in episodes if _.data_missing]:
        coroutines = [expand_episode(_) for _ in missing]
        expanded = await asyncio.gather(*coroutines)
        complete.extend(expanded)

    return sorted(complete, key=lambda x: x.date)


async def expand_episode(url_or_ep: str | Episode) -> Episode:
    if isinstance(url_or_ep, Episode):
        url = url_or_ep.url
    else:
        url = url_or_ep

    soup = await EpisodeSoup.from_url(url)
    res = Episode(**soup.get_ep_d())
    res.url = url
    return res


class EpisodeSoup(BeautifulSoup):
    def __init__(self, markup: str, parser: str = "html.parser", url=None):
        super().__init__(markup, parser)
        self.episode_url = url

    @property
    def episode_name(self):
        return self.select_one(".episode-title").text

    @property
    def episode_notes(self):
        paragraphs = self.select(".show-notes p")
        show_notes = [p.text for p in paragraphs if p.text != "Links"]

        return show_notes or None

    @property
    def episode_links(self):
        show_links_html = self.select(".show-notes a")
        show_links_dict = {aref.text: aref['href'] for aref in show_links_html}
        return show_links_dict

    @property
    def episode_date(self):
        date_st = self.select_one(".publish-date").text
        return parser.parse(date_st)

    def get_ep_d(self):
        episode = dict(
            name=self.episode_name,
            url=self.episode_url,
            notes=self.episode_notes,
            links=self.episode_links,
            date=self.episode_date
        )
        return episode

    @classmethod
    async def from_url(cls, url: str, aiosession: ClientSession = None) -> EpisodeSoup:
        aiosession = aiosession or ClientSession()
        async with aiosession:
            html = await _response(url, aiosession)
            soup = EpisodeSoup(html, "html.parser", url=url)
            return soup
