from __future__ import annotations

from datetime import datetime
from typing import Optional

from dateutil import parser
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel

from gurupod.gurulog import get_logger

logger = get_logger()
MAYBE_ATTRS = ["name", "notes", "links", "date"]


class Episode(SQLModel):
    url: str
    name: Optional[str] = Field(index=True, default=None, unique=True)
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)
    # gurus: List['GuruDB'] = Relationship(back_populates="episodes", link_model=GuruEpisodeLink)

    @field_validator("date", mode="before")
    def parse_date(cls, v) -> datetime:
        if isinstance(v, str):
            try:
                if len(v) == 10:
                    v = v + "T00:00:00"
                v = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except Exception:
                v = parser.parse(v)
                logger.warning(f"Could not parse date with standard format yyyy-mm-ddTHH:MM:SS - AutoParsed to {v}")
        return v

    @property
    def data_missing(self) -> bool:
        return any(getattr(self, _) is None for _ in MAYBE_ATTRS)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name or self.url}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.url})>"


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
