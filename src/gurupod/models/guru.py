# no dont do this!! from __future__ import annotations
"""sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize - can't proceed with initialization of other mappers. Triggering mapper: 'Mapper[Guru(guru)]'. Original exception was: When initializing mapper Mapper[Guru(guru)], expression "relationship("List['Episode']")" seems to be using a generic class as the argument to relationship(); please state the generic argument using an annotation, e.g. "episodes: Mapped[List['Episode']] = relationship()"
"""
from typing import List, Optional, TYPE_CHECKING

from pydantic import ConfigDict
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from .episode import Episode
    from .reddit_thread import RedditThread
from gurupod.models.links import GuruEpisodeLink, RedditThreadGuruLink


class GuruBase(SQLModel):
    name: Optional[str] = Field(index=True, default=None, unique=True)

    @property
    def slug(self):
        return f"/guru/{self.id}"


class Guru(GuruBase, table=True):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    episodes: List["Episode"] = Relationship(back_populates="gurus", link_model=GuruEpisodeLink)
    reddit_threads: List["RedditThread"] = Relationship(back_populates="gurus", link_model=RedditThreadGuruLink)


class GuruRead(GuruBase):
    id: int
