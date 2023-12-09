from datetime import datetime
from typing import Literal, Optional

import aiohttp
import requests
from bs4 import BeautifulSoup
from pydantic import field_validator, model_validator
from pydantic_core.core_schema import FieldValidationInfo
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel

from gurupod.scrape import deet_from_soup

MAYBE_ATTRS = ('notes', 'links', 'date', 'name')
MAYBE_TYPE = Literal['notes', 'links', 'date', 'name']

class EpisodeBase(SQLModel):
    url: str
    name: Optional[str] = Field(index=True, default=None, unique=True)
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)



class EpisodeIn(EpisodeBase):

    @field_validator('date', mode='before')
    def parse_date(cls, v) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v, '%Y-%m-%d')
        return v



class EpisodeDB(EpisodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class EpisodeOut(EpisodeIn):
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
