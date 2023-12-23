# from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from pydantic import ConfigDict
from sqlmodel import Field, Relationship, SQLModel

from gurupod.models.links import GuruEpisodeLink

if TYPE_CHECKING:
    from gurupod.models.episode import Episode


class GuruBase(SQLModel):
    name: Optional[str] = Field(index=True, default=None, unique=True)


class Guru(GuruBase, table=True):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    episodes: List["Episode"] = Relationship(back_populates="gurus", link_model=GuruEpisodeLink)


class GuruRead(GuruBase):
    id: int
