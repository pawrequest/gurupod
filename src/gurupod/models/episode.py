from datetime import datetime
from typing import Literal, Optional

from dateutil import parser
from pydantic import field_validator, model_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel


MAYBE_ATTRS = ('notes', 'links', 'date', 'name')
MAYBE_TYPE = Literal['notes', 'links', 'date', 'name']


class Episode(SQLModel):
    url: str
    name: Optional[str] = Field(index=True, default=None, unique=True)
    notes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    links: Optional[dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    date: Optional[datetime] = Field(default=None)

    @field_validator('date', mode='before')
    def parse_date(cls, v) -> datetime:
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d')
            except Exception:
                return parser.parse(v)
        return v

    # @model_validator(mode='before')
    # def maybe_expand(cls, v: dict, values):
    #     missing = []
    #     for name, attr in v.items():
    #         if attr is None:
    #             missing.append(MAYBE_ENUM(name))
    #
    #     v = expand_episode(v, missing)
    #     return v

    # async def expand_episode(ep: EPISODE_TYPE, aiosession: ClientSession) -> None:
    #     if missing := [_ for _ in MAYBE_ATTRS if getattr(ep, _) is None]:
    #         async with aiosession as aio_session:
    #             html = await _get_response(ep.url, aio_session)
    #             soup = BeautifulSoup(html, "html.parser")
    #             for attr in missing:
    #                 attr: MAYBE_LIT = attr  # apease the gods
    #                 setattr(ep, attr, deet_from_soup(attr, soup))


class EpisodeDB(Episode, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class EpisodeOut(Episode):
    id: int
    name: str
    url: str
    date: datetime
    notes: Optional[list[str]]
    links: Optional[dict[str, str]]

#
# def slugify(value: str) -> str:
#     """
#     Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
#     dashes to single dashes. Also strip leading and trailing whitespace, dashes,
#     and underscores.
#     """
#     value = str(value)
#     value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
#     value = re.sub(r'[^\w\s-]', '', value.lower())
#     return re.sub(r'[-\s]+', '-', value).strip('-_')
