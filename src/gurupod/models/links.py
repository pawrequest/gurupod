from __future__ import annotations

from typing import Optional

from sqlmodel import SQLModel, Field


# class GuruEpisodeLink(SQLModel, table=True):
#     guru_id: Optional[int] = Field(default=None, foreign_key="gurudb.id", primary_key=True)
#     episode_id: Optional[int] = Field(default=None, foreign_key="episodedb.id", primary_key=True)
#
