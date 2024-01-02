# from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Union

from dateutil import parser
from fastui.events import GoToEvent
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship
from loguru import logger
from fastui import components as c

from gurupod.core.database import SQLModel
from gurupod.core.consts import DEBUG
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink
from gurupod.ui.css import ROW
from gurupod.ui.shared import Col, Flex, Row, title_column, ui_link, play_column, master_self_only

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

    def ui_detail(self) -> Flex:
        return c.Details(data=self)
        # return Flex(
        #     components=[
        #         Row(
        #             components=[
        #                 c.Link(
        #                     components=[c.Text(text="Play")],
        #                     on_click=GoToEvent(url=self.url),
        #                 ),
        #             ]
        #         ),
        #         c.Paragraph(text=self.description),
        #     ]
        # )

    # ep page

    def ui_self_only(self, col=True) -> Union[c.Div, c.Link]:
        clink = ui_link(self.title, self.slug)
        return Col(components=[clink]) if col else clink

    def ui_with_related(self) -> c.Div:
        # guru_col = gurus_only(self.gurus, col=True)
        guru_col = master_self_only(self.gurus, col=True)
        title_col = title_column(self.title, self.slug)
        play_col = play_column(self.url)
        row = Row(classes=ROW, components=[guru_col, title_col, play_col])
        return row


class EpisodeRead(EpisodeBase):
    gurus: Optional[list[str]]
    reddit_threads: Optional[list[str]]
