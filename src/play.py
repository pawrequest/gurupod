from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI
from sqlalchemy import Column
from sqlmodel import Field, JSON, Relationship, SQLModel

from gurupod.database import create_db_and_tables


class GuruEpisodeLink(SQLModel, table=True):
    guru_id: Optional[int] = Field(default=None, foreign_key="guru.id", primary_key=True)
    episode_id: Optional[int] = Field(default=None, foreign_key="episode.id", primary_key=True)


class Guru(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    episodes: List[Episode] = Relationship(back_populates="gurus", link_model=GuruEpisodeLink)


class Episode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    name: Optional[str] = Field(index=True, default=None, unique=True)
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)

    gurus: list[Guru] = Relationship(back_populates="episodes", link_model=GuruEpisodeLink)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
