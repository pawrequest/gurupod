# from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from redditbot import RedditThread
from episode_scraper import Episode
from sqlmodel import Field, Relationship

from gurupod.core.database import SQLModel

if TYPE_CHECKING:
    pass


class GuruEpisodeLink(SQLModel, table=True):
    guru_id: Optional[int] = Field(default=None, foreign_key="guru.id", primary_key=True)
    episode_id: Optional[int] = Field(default=None, foreign_key="episode.id", primary_key=True)


class RedditThreadEpisodeLink(SQLModel, table=True):
    reddit_thread_id: Optional[int] = Field(default=None, foreign_key="redditthread.id", primary_key=True)
    episode_id: Optional[int] = Field(default=None, foreign_key="episode.id", primary_key=True)


class RedditThreadGuruLink(SQLModel, table=True):
    reddit_thread_id: Optional[int] = Field(default=None, foreign_key="redditthread.id", primary_key=True)
    guru_id: Optional[int] = Field(default=None, foreign_key="guru.id", primary_key=True)


class EpisodeWithLinks(Episode):
    gurus: Optional[List["Guru"]] = Relationship(back_populates="reddit_threads", link_model=RedditThreadGuruLink)
    ...


class RedditThreadWith(RedditThread):
    gurus: Optional[List["Guru"]] = Relationship(back_populates="reddit_threads", link_model=RedditThreadGuruLink)
    episodes: List["Episode"] = Relationship(back_populates="reddit_threads", link_model=RedditThreadEpisodeLink)

    # def ui_detail(self) -> Flex:
    #     return c.Details(data=self)
