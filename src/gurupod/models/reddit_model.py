from __future__ import annotations

from datetime import datetime
from typing import Optional

from asyncpraw.models import Submission
from sqlmodel import Field, Relationship

from gurupod.database import SQLModel
from gurupod.models.links import RedditThreadGuruLink


class RedditThreadBase(SQLModel):
    reddit_id: str
    title: str
    shortlink: str
    created_datetime: datetime


class RedditThread(RedditThreadBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    gurus: Optional[list["Guru"]] = Relationship(back_populates="reddit_threads", link_model=RedditThreadGuruLink)


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
