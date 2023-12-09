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

class EpisodeBase(SQLModel):
    url: str
    name: Optional[str] = Field(index=True, default=None, unique=True)
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)



class EpisodeIn(EpisodeBase):

    @model_validator(mode='after')
    def set_soup(cls, values):
        print(f'{type(values)=}')
        if missing := [_ for _ in cls.model_fields.keys() if getattr(values, _) is None]:

            # todo constrain get_deets to only MAYBE_ATTRS
            """
            strats: 1) iterate over maybe_attrs, if missing, get from soup
                        cant iterate over literal?
                    2) construct type from tuple
                        cant unpack into literal?
                """

            response = requests.get(values.url)
            soup = BeautifulSoup(response.text, "html.parser")

            # async with aiohttp.ClientSession() as session:
            #     async with session.get(values.url) as response:
            #         text = await response.text()
            # soup = BeautifulSoup(text, "html.parser")

            for key in missing:
                val = deet_from_soup(key, soup)
                if key == 'date':
                    val = datetime.strptime(val, '%Y-%m-%d')
                setattr(values, key, val)
                # [setattr(values, key, deet_from_soup(key, soup)) for key in missing]
        return values

    @field_validator('date', mode='before')
    def parse_date(cls, v):
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
