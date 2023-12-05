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
    notes: Optional[str] = Field(default=None)
    links: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    date_published: Optional[datetime] = Field(default=None)


class Episode(EpisodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class EpisodeCreate(EpisodeBase):
    async def get_data(self):
        if all([self.notes, self.links, self.date_published]):
            return

        async with (aiohttp.ClientSession() as session):
            async with session.get(self.url) as response:
                text = await response.text()
        soup = BeautifulSoup(text, "html.parser")
        self.notes = self.notes or '\n'.join(ep_soup_notes(soup))
        self.links = self.links or ep_soup_links(soup)
        self.date_published = self.date_published or ep_soup_date(soup)


class EpisodeRead(EpisodeBase):
    id: int
    date_published: datetime
