from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from dateutil import parser
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship, SQLModel

from gurupod.gurulog import logger
# from gurupod.models.links import GuruEpisodeLink

MAYBE_ATTRS = ['name', 'notes', 'links', 'date']


class Episode(SQLModel):
    url: str
    name: Optional[str] = Field(index=True, default=None, unique=True)
    notes: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[Dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)
    # gurus: List['GuruDB'] = Relationship(back_populates="episodes", link_model=GuruEpisodeLink)

    @field_validator('date', mode='before')
    def parse_date(cls, v) -> datetime:
        if isinstance(v, str):
            try:
                if len(v) == 10:
                    v = v + 'T00:00:00'
                    logger.debug('appending time')
                logger.debug(f'Parsing date: {v}')
                v = datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
                logger.debug(f'Parsed date: {v}')
            except Exception:
                logger.warning(f'Could not parse date: {v} with standard format %Y-%m-%dT%H:%M:%S')
                v = parser.parse(v)
                logger.info(f'Auto-parsed date: {v}')
        return v

    @property
    def data_missing(self) -> bool:
        return any(getattr(self, _) is None for _ in MAYBE_ATTRS)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.name or self.url}'

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.url})>'


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
