from typing import Optional

from sqlmodel import Field, Relationship

from gurupod.database import SQLModel
from gurupod.models.links import RedditThreadEpisodeLink, RedditThreadGuruLink


class RedditThreadBase(SQLModel):
    uri: str
    title: str


class RedditThread(RedditThreadBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    episodes: Optional[list["Episode"]] = Relationship(
        back_populates="reddit_threads", link_model=RedditThreadEpisodeLink
    )
    gurus: Optional[list["Guru"]] = Relationship(back_populates="reddit_threads", link_model=RedditThreadGuruLink)


class RedditThreadRead(RedditThreadBase):
    id: int
    title: str
    uri: str
