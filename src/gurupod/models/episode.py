from __future__ import annotations

import inspect
from datetime import datetime
from enum import Enum
from typing import Optional

from dateutil import parser
from pydantic import BaseModel, field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel

MAYBE_ATTRS = ['name', 'notes', 'links', 'date']
MAYBE_ENUM = Enum('MAYBE_ENUM', MAYBE_ATTRS)


class Episode(SQLModel):
    url: str
    name: Optional[str] = Field(index=True, default=None, unique=True)
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)

    @field_validator('date', mode='before')
    def parse_date(cls, v) -> datetime:
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d')
            except Exception:
                return parser.parse(v)
        return v

    @property
    def data_missing(self) -> bool:
        return any(getattr(self, _) is None for _ in MAYBE_ATTRS)


class EpisodeDB(Episode, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class EpisodeOut(Episode):
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
class EpisodeMeta(BaseModel):
    length: int
    calling_func: str
    msg: str = ''


class EpisodeResponse(BaseModel):
    meta: EpisodeMeta
    episodes: list[EpisodeOut]

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_episodes(cls, episodes: list[EpisodeDB], msg='') -> EpisodeResponse:
        if not isinstance(episodes, list):
            episodes = [episodes]
        valid = [EpisodeOut.model_validate(_) for _ in episodes]
        meta_data = EpisodeMeta(
            length=len(valid),
            calling_func=inspect.stack()[1][3],
            msg=msg
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))

    @classmethod
    def empty(cls, msg: str = 'No Episodes Found'):
        meta_data = EpisodeMeta(length=0, calling_func=inspect.stack()[1][3], msg=msg)
        return cls.model_validate(dict(episodes=[], meta=meta_data))

    @classmethod
    def no_new(cls):
        return cls.empty('No new episodes')

class EpisodeResponseNoDB(EpisodeResponse):
    episodes: list[Episode]
    @classmethod
    def from_episodes(cls, episodes: list[Episode], msg='') -> EpisodeResponse:
        if not isinstance(episodes, list):
            episodes = [episodes]
        valid = [Episode.model_validate(_) for _ in episodes]
        meta_data = EpisodeMeta(
            length=len(valid),
            calling_func=inspect.stack()[1][3],
            msg=msg
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))

