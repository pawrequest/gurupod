from __future__ import annotations

from typing import Optional, List

from sqlmodel import Field, Relationship, SQLModel

from gurupod.models.episode import EpisodeDB
# from gurupod.models.links import GuruEpisodeLink


# class GuruDB(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: Optional[str] = Field(index=True, default=None, unique=True)
#     episodes: List[EpisodeDB] = Relationship(back_populates="gurus", link_model=GuruEpisodeLink)
