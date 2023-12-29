from __future__ import annotations

from typing import List, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel

from gurupod.core.consts import DEBUG
from gurupod.core.gurulogging import get_logger, log_episodes
from gurupod.models.episode import Episode, EpisodeBase, EpisodeRead
from gurupod.models.guru import GuruBase, GuruRead
from gurupod.models.reddit_thread import RedditThreadBase, RedditThreadRead

logger = get_logger()


# keep 'with' views here for load order
class GuruWith(GuruBase):
    episodes: Optional[List["EpisodeRead"]]
    reddit_threads: Optional[List["RedditThreadRead"]]


class EpisodeWith(EpisodeBase):
    gurus: Optional[List["GuruRead"]]
    reddit_threads: Optional[List["RedditThreadRead"]]


class RedditThreadWith(RedditThreadBase):
    episodes: Optional[List["EpisodeRead"]]
    gurus: Optional[List["GuruRead"]]


EP_IN_DB_VAR = TypeVar("EP_IN_DB_VAR", bound=Union[Episode, EpisodeRead, EpisodeWith])
EP_OR_BASE_VAR = TypeVar("EP_OR_BASE_VAR", bound=Union[EpisodeBase, Episode, EpisodeRead, EpisodeWith])


class EpisodeMeta(BaseModel):
    length: int
    msg: str = ""


class EpisodeResponse(BaseModel):
    meta: EpisodeMeta
    episodes: list[EpisodeWith]

    @classmethod
    async def from_episodes(cls, episodes: Sequence[EP_OR_BASE_VAR], msg="") -> EpisodeResponse:
        eps = [EpisodeWith.model_validate(ep) for ep in episodes]
        if len(eps) == 0:
            msg = "No Episodes Found"
        meta_data = EpisodeMeta(
            length=len(eps),
            msg=msg,
        )
        res = cls.model_validate(dict(episodes=eps, meta=meta_data))
        if DEBUG:
            log_episodes(res.episodes, msg="Responding")
        return res

    def __str__(self):
        return f"{self.__class__.__name__}: {self.meta.length} {self.episodes[0].__class__.__name__}s"
