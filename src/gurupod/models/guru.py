# from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from gurupod.models.links import GuruEpisodeLink

if TYPE_CHECKING:
    from gurupod.models.episode import EpisodeDB


class Guru(SQLModel, table=True):
    # class Config:
    #     populate_by_name = True

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(index=True, default=None, unique=True)
    episodes: List["EpisodeDB"] = Relationship(back_populates="gurus", link_model=GuruEpisodeLink)


# class EpisodeDB(Episode, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     gurus: List[Guru] = Relationship(back_populates="episodes", link_model="GuruEpisodeLink")
#
#
