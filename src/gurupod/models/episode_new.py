from datetime import datetime
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel

from gurupod.scrape import ep_soup_date, ep_soup_links, ep_soup_notes


class EpisodeBase(SQLModel):
    name: str = Field(index=True, unique=True)
    url: str


class EpisodeCreate(EpisodeBase):
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date_published: Optional[datetime] = Field(default=None)


class Episode(EpisodeCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    @classmethod
    async def ep_scraped(cls, name, url):
        async with (aiohttp.ClientSession() as session):
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


class EpisodeRead(EpisodeBase):
    id: int
    date_published: datetime
    id: Optional[int]
    notes: Optional[list[str]]
    links: Optional[dict[str, str]]
    date_published: Optional[datetime]


async def ep_loaded(ep_dict: dict, name):
    try:
        return Episode(
            name=name,
            url=ep_dict.get('show_url'),
            notes=ep_dict.get('show_notes'),
            links=ep_dict.get('show_links'),
            date_published=datetime.strptime(ep_dict['show_date'], '%Y-%m-%d')
        )
    except Exception as e:
        ...
        raise Exception(f'FAILED TO ADD EPISODE {name}\nERROR:{e}')


async def ep_scraped(name, url):
    async with (aiohttp.ClientSession() as session):
        async with session.get(url) as response:
            text = await response.text()
    soup = BeautifulSoup(text, "html.parser")

    return Episode(
        name=name,
        url=url,
        notes=ep_soup_notes(soup),
        links=ep_soup_links(soup),
        date_published=ep_soup_date(soup),
    )
