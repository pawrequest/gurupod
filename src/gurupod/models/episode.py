# from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Union

from dateutil import parser
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship
from loguru import logger
from fastui import components as c

from gurupod.core.database import SQLModel
from gurupod.core.consts import DEBUG
from gurupod.episode_monitor.writer import RPostWriter
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink
from gurupod.ui.css import ROW
from gurupod.ui.shared import Col, Flex, Row, object_ui_self_only, play_column, title_column, ui_link

if TYPE_CHECKING:
    from gurupod.models.guru import Guru
    from gurupod.models.reddit_thread import RedditThread

MAYBE_ATTRS = ["title", "notes", "links", "date"]


class EpisodeBase(SQLModel):
    url: str = Field(index=True)
    title: str = Field(index=True)
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)
    episode_number: str

    @field_validator("episode_number", mode="before")
    def ep_number_is_str(cls, v) -> str:
        return str(v)

    @field_validator("date", mode="before")
    def parse_date(cls, v) -> datetime:
        if isinstance(v, str):
            try:
                v = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except Exception:
                v = parser.parse(v)
                if DEBUG:
                    logger.debug(f"AutoParsed Date to {v}")
        return v

    def log_str(self) -> str:
        if self.title and self.date:
            return f"\t\t<green>{self.date.date()}</green> - <bold><cyan>{self.title}</cyan></bold>"
        else:
            return f"\t\t{self.url}"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.title or self.url}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.url})>"

    @property
    def slug(self):
        return f"/eps/{self.id}"


class Episode(EpisodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gurus: Optional[List["Guru"]] = Relationship(back_populates="episodes", link_model=GuruEpisodeLink)
    reddit_threads: Optional[List["RedditThread"]] = Relationship(
        back_populates="episodes", link_model=RedditThreadEpisodeLink
    )

    def ui_detail(self) -> Flex:
        writer = RPostWriter(self)
        markup = writer.write_one()
        return Flex(
            components=[
                *(_.ui_self_only() for _ in self.gurus),
                c.Markdown(text=markup),
            ]
        )

    def ui_self_only(self) -> Union[c.Div, c.Link]:
        clink = ui_link(self.title, self.slug)
        # return clink
        return Col(components=[clink])

    def ui_with_related(self) -> c.Div:
        guru_col = object_ui_self_only(self.gurus)
        title_col = title_column(self.title, self.slug)
        play_col = play_column(self.url)
        row = Row(classes=ROW, components=[guru_col, title_col, play_col])
        return row


class EpisodeRead(EpisodeBase):
    gurus: Optional[list[str]]
    reddit_threads: Optional[list[str]]
