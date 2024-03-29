# no dont do this!! from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from asyncpraw.models import Submission
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship, SQLModel
from fastui import components as c

from gurupod.models.links import RedditThreadEpisodeLink, RedditThreadGuruLink
from gurupod.ui.mixin import Flex

if TYPE_CHECKING:
    from gurupod.models.guru import Guru
    from gurupod.models.episode import Episode


def submission_to_dict(submission: dict | Submission):
    serializable_types = (int, float, str, bool, type(None))
    if isinstance(submission, Submission):
        submission = vars(submission)
    return {k: v for k, v in submission.items() if isinstance(v, serializable_types)}


class RedditThreadBase(SQLModel):
    class Config:
        arbitrary_types_allowed = True

    reddit_id: str = Field(index=True, unique=True)
    title: str
    shortlink: str
    created_datetime: datetime
    submission: Submission | dict = Field(sa_column=Column(JSON))

    @field_validator("submission", mode="before")
    def validate_submission(cls, v):
        return submission_to_dict(v)

    @classmethod
    def from_submission(cls, submission: Submission):
        tdict = dict(
            reddit_id=submission.id,
            title=submission.title,
            shortlink=submission.shortlink,
            created_datetime=submission.created_utc,
            submission=submission,
        )
        return cls.model_validate(tdict)

    @classmethod
    def from_submission_plus(cls, submission: Submission):
        tdict = dict(
            reddit_id=submission.id,
            title=submission.title,
            shortlink=submission.shortlink,
            created_datetime=submission.created_utc,
            submission=submission,
        )
        return cls.model_validate(tdict)

    @property
    def slug(self):
        return f"/red/{self.id}"


class RedditThread(RedditThreadBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gurus: Optional[List["Guru"]] = Relationship(back_populates="reddit_threads", link_model=RedditThreadGuruLink)
    episodes: List["Episode"] = Relationship(back_populates="reddit_threads", link_model=RedditThreadEpisodeLink)

    def ui_detail(self) -> Flex:
        return c.Details(data=self)


class RedditThreadRead(RedditThreadBase):
    id: int
