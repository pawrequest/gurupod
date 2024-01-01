# from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from dateutil import parser
from fastui.events import GoToEvent
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship
from loguru import logger
from fastui import components as c, AnyComponent

from gurupod.core.database import SQLModel
from gurupod.core.consts import DEBUG
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink
from gurupod.shared import Col, Flex

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


class Episode(EpisodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gurus: Optional[List["Guru"]] = Relationship(back_populates="episodes", link_model=GuruEpisodeLink)
    reddit_threads: Optional[List["RedditThread"]] = Relationship(
        back_populates="episodes", link_model=RedditThreadEpisodeLink
    )


class EpisodeRead(EpisodeBase):
    # title: str
    # url: str
    # date: datetime
    # notes: Optional[list[str]]
    # links: Optional[dict[str, str]]
    gurus: Optional[list[str]]
    reddit_threads: Optional[list[str]]

    # @field_validator("gurus", mode="before")
    # def gurus_to_list(cls, v) -> list[str]:
    #     if isinstance(v, list) and v:
    #         logger.debug("Converting Guru to str")
    #         v = [g.name for g in v]
    #     return v

    # @field_validator("reddit_threads", mode="before")
    # def reddit_threads_to_list(cls, v) -> list[str]:
    #     if isinstance(v, list) and v:
    #         logger.debug("Converting RedditThread to str")
    #         v = [t.url for t in v]
    #     return v


class EpisodeFE(EpisodeBase):
    id: int
    # title: str
    # url: str
    # date: datetime
    # notes: Optional[list[str]]
    # links: Optional[ContentLinkCollection]
    links: Optional[dict[str, str]]
    gurus: Optional[list[str]]
    reddit_threads: Optional[list[str]]

    @property
    def slug(self):
        return f"/eps/{self.id}"

    @field_validator("gurus", mode="before")
    def gurus_to_list(cls, v) -> list[str]:
        if isinstance(v, list) and v:
            try:
                v = [g.name for g in v]
                logger.debug(f"Converting Guru to str {v}")
            except Exception as e:
                logger.error(f"Could not convert Gurus to list: {v} - {e}")
        return v

    @field_validator("reddit_threads", mode="before")
    def reddit_threads_to_list(cls, v) -> list[str]:
        if isinstance(v, list) and v:
            logger.debug("Converting RedditThread to str")
            v = [t.url for t in v]
        return v

    def to_div(self) -> Flex:
        return Flex(
            components=[
                self.gurus_col(),
                self.title_col(),
                self.captive_col(),
            ]
        )

    def joining_string(self) -> AnyComponent:
        return c.Text(text=",   ")

    def join_components_if_multiple(self, components: list[AnyComponent]) -> list[AnyComponent]:
        if len(components) < 2:
            return components
        else:
            res = []
            for component in components[:-1]:
                res.extend([component, self.joining_string()])
            res.append(components[-1])
            return res
            # res = [[component, self.joining_string()] for component in components[:-1]]
            # return res + [components[-1]]

    def gurus_col(self):
        return Col(
            classes=["col-3"],
            components=[
                # c.Text(text=", ".join([f"[{g}](/gurus/{g})" for g in self.gurus])),
                Col(
                    components=self.join_components_if_multiple(
                        [
                            c.Link(
                                components=[c.Text(text=g)],
                                on_click=GoToEvent(url=f"/gurus/{g}"),
                            )
                            for g in self.gurus
                        ]
                    )
                )
            ],
        )
        # class_name="text-left col-3",
        # components=[c.Markdown(text=", ".join([f'[{g}]({f"/gurus/{g}"})' for g in self.gurus]))],
        # c.Link(components=[c.Text(text=g)], on_click=GoToEvent(url=f"/gurus/{g}"))
        # c.Markdown(text=f"[{g}]({f'/gurus/{g}'})")
        # c.Markdown(text=f"{[
        #     f'[{g}]({f'/gurus/{g}'})'
        #     for g in self.gurus
        # ]}")
        # for g in self.gurus
        #     ],
        # )

    def title_col(self):
        return Col(
            classes=["col-6"],
            # class_name="col-6 text-center",
            components=[
                c.Link(
                    components=[c.Text(text=self.title)],
                    on_click=GoToEvent(url=self.slug),
                    # class_name="text-primary bg-light",
                ),
            ],
        )

    def captive_col(self):
        return Col(
            classes=["col-3"],
            components=[
                c.Link(
                    components=[c.Text(text="Play on Captivate.fm")],
                    on_click=GoToEvent(url=self.url),
                    # class_name="text-right",
                ),
            ],
        )

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

    """

    ------------------------------------------------------------DTG Christmas Quiz 2023 with Helen Lewis — Play on Captivate.fm

    ----------------------------------------------Red Scare: Bohemian Hipsterism x Reactionary Tradcaths — Play on Captivate.fm

    ----------------------------Interview with Daniël Lakens and Smriti Mehta on the state of Psychology — Play on Captivate.fm

    -------------------------Andrew Huberman and Peter Attia: Self-enhancement, supplements & doughnuts? — Play on Captivate.fm

    -------------------------------------Interview with Julia Ebner: Extremist Networks & Radicalisation — Play on Captivate.fm

    -----------------------------------------------Triggernometry's Big Moment: Entering the Guru Galaxy — Play on Captivate.fm

    -----------------------Interview with the Conspirituality Trio: Navigating the Chakras of Conspiracy — Play on Captivate.fm

    """

    # @property
    # def to_markdown(self) -> str:
    #     res = f"""* `[{self.title}]({self.slug})`— [Play on Captivate.fm](self.url)
    #     """
    #
    #     return f"[{self.title}]({self.url})"

    # @field_validator("url", mode="before")
    # def url_to_link(cls, v, values) -> c.Link:
    #     if isinstance(v, str):
    #         logger.debug("Converting str to c.Link")
    #         v = c.Link(components=[c.Text(text=f'Play on Captivate.fm')], on_click=GoToEvent(url=v))
    #     return v

    # class EpisodeFEold(EpisodeBase):
    #     title: str
    #     url: str
    #     date: datetime
    #     notes: Optional[list[str]]
    #     links: Optional[dict[str, str]]
    #     gurus: Optional[list[str]]
    #     reddit_threads: Optional[list[str]]
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
