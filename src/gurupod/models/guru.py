from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from gurupod.models.episode import Episode


class Guru(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    episodes: List["Episode"] = Relationship(back_populates="gurus", link_model="GuruEpisodeLink")


class GuruEpisodeLink(SQLModel, table=True):
    guru_id: Optional[int] = Field(default=None, foreign_key="guru.id", primary_key=True)
    episode_id: Optional[int] = Field(default=None, foreign_key="episode.id", primary_key=True)


class EpisodeDB(Episode, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gurus: List["Guru"] = Relationship(back_populates="episodes", link_model="GuruEpisodeLink")
