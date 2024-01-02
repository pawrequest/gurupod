# no dont do this!! from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Union

from asyncpraw.models import Submission
from fastui.events import GoToEvent
from loguru import logger
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship, SQLModel
from fastui import components as c

from gurupod.models.links import RedditThreadEpisodeLink, RedditThreadGuruLink
from gurupod.ui.css import ROW
from gurupod.ui.shared import Col, Flex, Row, ui_link, master_self_only

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

    def ui_detail(self, container=False) -> Flex:
        return c.Details(data=self)
        # return Flex(
        #     components=[
        #         Row(
        #             components=[
        #                 c.Link(
        #                     components=[c.Text(text="reddit")],
        #                     on_click=GoToEvent(url=self.shortlink),
        #                 )
        #             ]
        #         ),
        #         c.Paragraph(text=self.submission.get("selftext")),
        #     ]
        # )

    def ui_with_related(self) -> Row:
        red_col = self.ui_self_only(col=True)
        guru_col = master_self_only(self.gurus, col=True)
        # guru_col = gurus_only(self.gurus, col=True)
        ep_col = master_self_only(self.episodes, col=True)
        # ep_col = episodes_only(self.episodes)
        return Row(classes=ROW, components=[red_col, guru_col, ep_col])

    def ui_self_only(self, col=False) -> Union[c.Div, c.Link]:
        reddit_link = ui_link(self.title, self.slug)
        if col:
            reddit_link = Col(components=[reddit_link])

        return reddit_link


class RedditThreadRead(RedditThreadBase):
    id: int


class RedditThreadFE(RedditThreadBase):
    id: int
    gurus: Optional[list[str]]
    episodes: Optional[list[str]]

    @field_validator("gurus", mode="before")
    def gurus_to_list(cls, v) -> list[str]:
        if isinstance(v, list) and v:
            try:
                v = [g.name for g in v]
                logger.debug("Thread Converting Guru to str")
            except Exception as e:
                logger.error(f"Could not convert Gurus to list: {v} - {e}")
        return v

    @field_validator("episodes", mode="before")
    def reddit_threads_to_list(cls, v) -> list[str]:
        if isinstance(v, list) and v:
            logger.debug("Thnread Converting episode to str")
            try:
                v = [t.url for t in v]
            except Exception as e:
                logger.error(f"Could not convert Episodes to list: {v} - {e}")
        return v
