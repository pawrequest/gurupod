from __future__ import annotations

from typing import AsyncGenerator, List, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel, ValidationError

from gurupod.gurulog import get_logger
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
    # _submission: Optional["Submission"]


EP_IN_DB_TYP = Union[EpisodeRead, Episode, EpisodeWith]
EP_OR_BASE_TYP = Union[EpisodeBase, EP_IN_DB_TYP]
EP_IN_DB_VAR = TypeVar("EP_IN_DB_VAR", bound=EP_IN_DB_TYP)
EP_OR_BASE_VAR = TypeVar("EP__OR_BASE_VAR", bound=EP_OR_BASE_TYP)


# def validate_episode(episode: EP_OR_BASE_VAR) -> EP_OR_BASE_VAR:
#     try:
#         return EpisodeRead.model_validate(episode)
#     except Exception as e:
#         try:
#             return Episode.model_validate(episode)
#         except Exception:
#             raise ValueError(f"episodes must be {EP_OR_BASE_TYP} or Sequence-of, not {type(episode)}")


def validate_ep_or_base(episode) -> Episode | EpisodeRead:
    try:
        res = EpisodeRead.model_validate(episode)
    except ValidationError as e:
        res = Episode.model_validate(episode)
    return res


# async def repack_validate_old(
#     episodes: EP_OR_BASE_VAR | Sequence[EP_OR_BASE_VAR],
# ) -> AsyncGenerator[EP_OR_BASE_VAR, None]:
#     """Takes episode or sequence, checks type, returns tuple of episodes."""
#     if not isinstance(episodes, Sequence):
#         episodes = (episodes,)
#     for ep in episodes:
#         yield validate_ep_or_base(ep)


# async def repack_validate_async(episodes: AsyncGenerator[EP_OR_BASE_VAR, None]) -> AsyncGenerator[EP_OR_BASE_VAR, None]:
#     logger.debug("repack_validate_async")
#     async for ep in episodes:
#         logger.debug(f"repack_validate_async in loop: {ep}")
#         yield validate_ep_or_base(ep)


# def repack_validate(episodes: EP_OR_BASE_VAR | Sequence[EP_OR_BASE_VAR]) -> tuple[EP_OR_BASE_VAR, ...]:
#     """Takes episode or sequence, checks type, returns tuple of episodes."""
#     if not isinstance(episodes, Sequence):
#         episodes = (episodes,)
#     validated_episodes = tuple(validate_ep_or_base(ep) for ep in episodes)
#     # validated_episodes = tuple(validate_episode(ep) for ep in episodes)
#     return validated_episodes


class EpisodeMeta(BaseModel):
    length: int
    msg: str = ""


class EpisodeResponse(BaseModel):
    meta: EpisodeMeta
    episodes: list[EpisodeWith]

    @classmethod
    async def from_episodes_seq(cls, episodes: Sequence[EP_OR_BASE_VAR], msg="") -> EpisodeResponse:
        eps = [ep for ep in episodes]
        if len(eps) == 0:
            msg = "No Episodes Found"
        meta_data = EpisodeMeta(
            length=len(eps),
            msg=msg,
        )
        return cls.model_validate(dict(episodes=eps, meta=meta_data))

    def __str__(self):
        return f"{self.__class__.__name__}: {self.meta.length} {self.episodes[0].__class__.__name__}s"
