from datetime import datetime
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel

from gurupod.scrape import ep_soup_date, ep_soup_links, ep_soup_notes


class EpisodeBase(SQLModel):
    name: str = Field(index=True, unique=True)
    url: str


class EpisodeCreate(EpisodeBase):
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)

    @field_validator('date', mode='before')
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, '%Y-%m-%d')
        return v



    # slug: Optional[str] = Field(default=None)
    #
    # @field_validator('slug', mode='after')
    # def create_slug(cls, v, values):
    #     if 'title' in values:
    #         return slugify(values['title'])
    #     return v
    #


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
            date=ep_soup_date(soup),
        )

    @classmethod
    async def ep_loaded(cls, ep_dict: dict):
        try:
            return cls(
                name=ep_dict.get('name'),
                url=ep_dict.get('url'),
                notes=ep_dict.get('notes'),
                links=ep_dict.get('links'),
                date=datetime.strptime(ep_dict['date'], '%Y-%m-%d')
            )
        except Exception as e:
            ...
            raise Exception(f'FAILED TO ADD EPISODE {ep_dict=}\nERROR:{e}')

    @classmethod
    async def ep_loadedold(cls, ep_dict: dict, name):
        try:
            return cls(
                name=name,
                url=ep_dict.get('url'),
                notes=ep_dict.get('notes'),
                links=ep_dict.get('links'),
                date=datetime.strptime(ep_dict['date'], '%Y-%m-%d')
            )
        except Exception as e:
            ...
            raise Exception(f'FAILED TO ADD EPISODE {name}\nERROR:{e}')


class EpisodeRead(EpisodeBase):
    id: int
    name: str
    url: str
    date: datetime
    notes: Optional[list[str]]
    links: Optional[dict[str, str]]

#
# def slugify(value: str) -> str:
#     """
#     Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
#     dashes to single dashes. Also strip leading and trailing whitespace, dashes,
#     and underscores.
#     """
#     value = str(value)
#     value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
#     value = re.sub(r'[^\w\s-]', '', value.lower())
#     return re.sub(r'[-\s]+', '-', value).strip('-_')
