from datetime import datetime
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
from fastapi import Depends
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel, Session

from gurupod.scrape import ep_soup_date, ep_soup_links, ep_soup_notes


class EpisodeBase(SQLModel):
    name: str = Field(index=True, unique=True)
    url: str


class Episode(EpisodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    date_published: Optional[datetime] = Field(default=None)

    @classmethod
    async def ep_scraped(cls, name, url, session):
        async with session.get(url) as response:
            text = await response.text()
        soup = BeautifulSoup(text, "html.parser")

        return cls(
            name=name,
            url=url,
            notes=ep_soup_notes(soup),
            links=ep_soup_links(soup),
            date_published=ep_soup_date(soup),
        )

    @classmethod
    async def ep_loaded(cls, ep_dict: dict, name):
        try:
            return cls(
                name=name,
                url=ep_dict.get('show_url'),
                notes=ep_dict.get('show_notes'),
                links=ep_dict.get('show_links'),
                date_published=datetime.strptime(ep_dict['show_date'], '%Y-%m-%d')
            )
        except Exception as e:
            ...
            raise Exception(f'FAILED TO ADD EPISODE {name}\nERROR:{e}')


#
# class EpisodeCreate(EpisodeBase):
#     def __init__(self, **data):
#         super().__init__(**data)
#         self.get_data()
#
#     async def get_data(self):
#         if all([self.notes, self.links, self.date_published]):
#             return
#
#         async with (aiohttp.ClientSession() as session):
#             async with session.get(self.url) as response:
#                 text = await response.text()
#         soup = BeautifulSoup(text, "html.parser")
#         self.notes = self.notes or ep_soup_notes(soup)
#         self.links = self.links or ep_soup_links(soup)
#         self.date_published = self.date_published or ep_soup_date(soup)
#
#
# class EpisodeCreate(EpisodeBase):
#     async def get_data(self):
#         async with aiohttp.ClientSession() as session:
#             async with session.get(self.url) as response:
#                 text = await response.text()
#         soup = BeautifulSoup(text, "html.parser")
#         self.notes = ep_soup_notes(soup)
#         self.links = ep_soup_links(soup)
#         self.date_published = ep_soup_date(soup)
#
#         return Episode(
#             name=self.name,
#             url=self.url,
#             notes=self.notes,
#             links=self.links,
#             date_published=self.date_published
#         )
#

class EpisodeRead(Episode):
    id: int
    date_published: datetime

