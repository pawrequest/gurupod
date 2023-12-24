# no dont do this!! from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from asyncpraw.models import Submission
from sqlmodel import Field, Relationship

from gurupod.database import SQLModel
from gurupod.models.links import RedditThreadEpisodeLink, RedditThreadGuruLink

if TYPE_CHECKING:
    from gurupod.models.guru import Guru, Episode


class RedditThreadBase(SQLModel):
    reddit_id: str
    title: str
    shortlink: str
    created_datetime: datetime


class RedditThread(RedditThreadBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    _submission: Optional[Submission] = None
    gurus: Optional[List["Guru"]] = Relationship(back_populates="reddit_threads", link_model=RedditThreadGuruLink)
    episodes: List["Episode"] = Relationship(back_populates="reddit_threads", link_model=RedditThreadEpisodeLink)


class RedditThreadRead(RedditThreadBase):
    id: int


class RedditThreadExpanded(RedditThreadBase):
    _submission: Submission = None

    @classmethod
    def from_id(cls, reddit, submission_id: str):
        submission = Submission(id=submission_id, reddit=reddit)
        tdict = dict(
            reddit_id=submission.id,
            title=submission.title,
            shortlink=submission.shortlink,
            created_datetime=submission.created_utc,
            _submission=submission,
        )
        return cls.model_validate(tdict)

    @classmethod
    def from_submission(cls, submission: Submission):
        tdict = dict(
            reddit_id=submission.id,
            title=submission.title,
            shortlink=submission.shortlink,
            created_datetime=submission.created_utc,
            _submission=submission,
        )
        return cls.model_validate(tdict)
