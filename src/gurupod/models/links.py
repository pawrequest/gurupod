# from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlmodel import Field
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
