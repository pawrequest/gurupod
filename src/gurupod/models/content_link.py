from typing import Optional

from loguru import logger
from pydantic import model_validator
from sqlmodel import Field, SQLModel


# class ContentTypes(str, StrEnum):
#     text = auto()
#     image = auto()
#     video = auto()
#     audio = auto()
#     social = auto()


# class ContentLink(SQLModel):
#     url: str = Field(index=True)
#     title: str = Field(index=True)
#     description: Optional[str] = None
#     # content_type: ContentTypes = Field(index=True)
#
#     # @model_validator(mode="before")
#     # def url_is_str(cls, v) -> str:
#     #     return str(v)


# class ContentLinkCollection(SQLModel):
#     c_links: list["ContentLink"] = Field(default_factory=list)
#
#     @model_validator(mode="before")
#     def links_to_list(cls, v, values):
#         links_ = v.get("links")
#         if not links_:
#             v["links"] = []
#             return v
#         if isinstance(v, dict) or isinstance(links_, dict):
#             logger.debug("Converting dict to list")
#             links_ = [ContentLink(url=url, title=title) for title, url in links_.items()]
#             v["links"] = links_
#         return v
