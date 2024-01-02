# from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from dateutil import parser
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship
from loguru import logger

from gurupod.core.database import SQLModel
from gurupod.core.consts import DEBUG
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink
from gurupod.ui.shared import Flex, title_column, gurus_column
from gurupod.ui.episode_view import play_column

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

    @property
    def to_markdown(self) -> str:
        res = f"""* {self.slug_md} -- {self.gurus} -- {self.captivate_md}
    """

        return res

    @property
    def captivate_md(self):
        return f"[Play on Captivate.fm]({self.url})"

    @property
    def slug_md(self):
        pad = 150 - len(self.title)
        return f"[{self.title:{pad}}]({self.slug})"


class Episode(EpisodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gurus: Optional[List["Guru"]] = Relationship(back_populates="episodes", link_model=GuruEpisodeLink)
    reddit_threads: Optional[List["RedditThread"]] = Relationship(
        back_populates="episodes", link_model=RedditThreadEpisodeLink
    )
    #
    # def to_div(self) -> Flex:
    #     return Flex(
    #         classes=["row", "my-2"],
    #         components=[
    #             gurus_div(self.gurus),
    #             title_div(self.title, self.slug),
    #             play_div(self),
    #         ],
    #     )
    #


class EpisodeRead(EpisodeBase):
    gurus: Optional[list[str]]
    reddit_threads: Optional[list[str]]


# class EpisodeFE(EpisodeBase):
#     id: int
#     links: Optional[dict[str, str]]
#     gurus: Optional[list[str]]
#     reddit_threads: Optional[list[str]]


# @field_validator("gurus", mode="before")
# def gurus_to_list(cls, v) -> list[str]:
#     if isinstance(v, list) and v:
#         try:
#             v = [g.name for g in v]
#             logger.debug(f"Converting Guru to str {v}")
#         except Exception as e:
#             logger.error(f"Could not convert Gurus to list: {v} - {e}")
#     return v
#
# @field_validator("reddit_threads", mode="before")
# def reddit_threads_to_list(cls, v) -> list[str]:
#     if isinstance(v, list) and v:
#         logger.debug("Converting RedditThread to str")
#         v = [t.url for t in v]
#     return v

# class EpisodeFE(EpisodeBase):
#     id: int
#     links: Optional[dict[str, str]]
#     gurus: Optional[list[str]]
#     reddit_threads: Optional[list[str]]
#
#     @property
#     def slug(self):
#         return f"/eps/{self.id}"
#
#     @field_validator("gurus", mode="before")
#     def gurus_to_list(cls, v) -> list[str]:
#         if isinstance(v, list) and v:
#             try:
#                 v = [g.name for g in v]
#                 logger.debug(f"Converting Guru to str {v}")
#             except Exception as e:
#                 logger.error(f"Could not convert Gurus to list: {v} - {e}")
#         return v
#
#     @field_validator("reddit_threads", mode="before")
#     def reddit_threads_to_list(cls, v) -> list[str]:
#         if isinstance(v, list) and v:
#             logger.debug("Converting RedditThread to str")
#             v = [t.url for t in v]
#         return v
#
#     @property
#     def to_markdown(self) -> str:
#         res = f""" * {self.slug_md} - - {self.gurus} - - {self.captivate_md}
#
#
#         return res
#
#     @property
#     def captivate_md(self):
#         return f"[Play on Captivate.fm]({self.url})"
#
#     @property
#     def slug_md(self):
#         pad = 150 - len(self.title)
#         return f"[{self.title:{pad}}]({self.slug})"
#
#     def to_div(self) -> Flex:
#         return Flex(
#             classes=["row", "my-2"],
#             components=[
#                 gurus_div(self.gurus),
#                 title_div(self.title, self.slug),
#                 play_div(self.url),
#             ],
#         )
