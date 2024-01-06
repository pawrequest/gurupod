# from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from dateutil import parser
from episode_scraper.episode_model import EpisodeBase, RPostWriter
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship
from loguru import logger
from fastui import components as c

from gurupod.core.database import SQLModel
from gurupod.core.consts import DEBUG
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink
from gurupod.ui.mixin import Flex, _object_ui

if TYPE_CHECKING:
    from gurupod.models.guru import Guru
    from redditbot import RedditThread

MAYBE_ATTRS = ["title", "notes", "links", "date"]


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
                *(_object_ui(_) for _ in self.gurus),
                c.Markdown(text=markup),
            ]
        )


class EpisodeRead(EpisodeBase):
    gurus: Optional[list[str]]
    reddit_threads: Optional[list[str]]
