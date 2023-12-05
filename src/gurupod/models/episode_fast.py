from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, NamedTuple, Optional

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser
from fastapi import FastAPI
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel, Session, create_engine, select


class EpisodeBase(SQLModel):
    name: str = Field(index=True, unique=True)
    url: str
    notes: Optional[str] = Field(default=None)
    links: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    date_published: Optional[datetime] = Field(default=None)


class Episode(EpisodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class EpisodeCreate(EpisodeBase):
    async def get_data(self):
        if all([self.notes, self.links, self.date_published]):
            return

        async with (aiohttp.ClientSession() as session):
            async with session.get(self.url) as response:
                text = await response.text()
        soup = BeautifulSoup(text, "html.parser")
        ep_details_ = EpDetails.from_soup(soup)
        self.notes = self.notes or '\n'.join(ep_details_.notes)
        self.links = self.links or ep_details_.links
        self.date_published = self.date_published or ep_details_.date


class EpisodeRead(EpisodeBase):
    id: int
    date_published: datetime


sqlite_file_name = "epi-fast.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/eps/", response_model=EpisodeRead)
async def create_episode(episode: EpisodeCreate):
    await episode.get_data()

    with Session(engine) as session:
        db_ep = Episode.model_validate(episode)
        session.add(db_ep)
        session.commit()
        session.refresh(db_ep)
        return db_ep


@app.get("/eps/", response_model=List[EpisodeRead])
def read_episodes():
    with Session(engine) as session:
        episodes = session.exec(select(Episode)).all()
        return episodes


class EpDetails(NamedTuple):
    notes: list
    links: dict
    date: datetime.date

    @classmethod
    def from_soup(cls, ep_soup):
        """ ep_soup is a complete episode-specific page"""
        return cls(
            notes=ep_soup_notes(ep_soup),
            links=ep_soup_links(ep_soup),
            date=ep_soup_date(ep_soup),
        )


def ep_soup_date(ep_soup) -> datetime:
    date_str = ep_soup.select_one(".publish-date").text
    datey = parser.parse(date_str)
    return datey


def ep_soup_notes(soup: BeautifulSoup) -> list:
    """ some listing have literal("Links") as heading for next section some dont """

    paragraphs = soup.select(".show-notes p")
    show_notes = [p.text for p in paragraphs if p.text != "Links"]

    return show_notes


def ep_soup_links(soup: BeautifulSoup) -> dict:
    show_links_html = soup.select(".show-notes a")
    show_links_dict = {aref.text: aref['href'] for aref in show_links_html}
    return show_links_dict

# class Link(SQLModel, table=True):
#     name: Optional[str] = models.CharField(max_length=200)
#     url = models.URLField(unique=True)
# slug = models.SlugField(editable=False, unique=True)
# narrative = models.TextField(null=True, blank=True)
# tags = models.ManyToManyField('Tag', related_name='link_tags', blank=True)
# gurus = models.ManyToManyField('Guru', related_name='guru_links', blank=True)
#
# def save(self, *args, **kwargs):
#     self.slug = slugify(self.name)
#     self.url = self.url.lower()
#     super().save(*args, **kwargs)
#
# def __str__(self):
#     return self.name

# def get_absolute_url(self):
#     return reverse("link_detail", args=[self.slug])

# @field_validator(__field='show_date', mode='before')
# def parse_date(cls, v):
#     if isinstance(v, datetime):
#         return v
#     return datetime.strptime(v, "%Y-%m-%d").date()
#
# @field_validator(__field='show_notes', mode='before')
# def parse_notes(cls, v):
#     if isinstance(v, list):
#         v = '\n'.join(v)
#     return v
#
# @field_validator(__field='show_links', mode='before')
# def parse_links(cls, v):
#     if isinstance(v, dict):
#         v = json.dumps(v)
#     return v

#
