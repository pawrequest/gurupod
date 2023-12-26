from __future__ import annotations

from typing import AsyncGenerator, List, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel

from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode, EpisodeBase, EpisodeRead
from gurupod.models.guru import GuruBase, GuruRead
from gurupod.models.reddit_model import RedditThreadBase, RedditThreadRead

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


def validate_episode(episode: EP_OR_BASE_VAR) -> EP_OR_BASE_VAR:
    try:
        return EpisodeRead.model_validate(episode)
    except Exception as e:
        try:
            return Episode.model_validate(episode)
        except Exception:
            raise ValueError(f"episodes must be {EP_OR_BASE_TYP} or Sequence-of, not {type(episode)}")


async def validate_ep_or_base(episode):
    try:
        return EpisodeRead.model_validate(episode)
    except Exception as e:
        # which exception??
        try:
            return Episode.model_validate(episode)
        except Exception:
            raise ValueError(f"episodes must be {EP_OR_BASE_TYP} or Sequence-of, not {type(episode)}")


async def repack_validatenew(
    episodes: EP_OR_BASE_VAR | Sequence[EP_OR_BASE_VAR],
) -> AsyncGenerator[EP_OR_BASE_VAR, None]:
    """Takes episode or sequence, checks type, returns tuple of episodes."""
    if not isinstance(episodes, Sequence):
        episodes = (episodes,)
    for ep in episodes:
        yield await validate_ep_or_base(ep)


async def repack_validate_async(episodes: AsyncGenerator[EP_OR_BASE_VAR, None]) -> AsyncGenerator[EP_OR_BASE_VAR, None]:
    if not isinstance(episodes, Sequence):
        episodes = (episodes,)
    for ep in episodes:
        yield await validate_ep_or_base(ep)

    # validated_episodes = tuple(await validate_episode(ep) for ep in episodes)
    # # validated_episodes = tuple(validate_episode(ep) for ep in episodes)
    # return validated_episodes


def repack_validate(episodes: EP_OR_BASE_VAR | Sequence[EP_OR_BASE_VAR]) -> tuple[EP_OR_BASE_VAR, ...]:
    """Takes episode or sequence, checks type, returns tuple of episodes."""
    if not isinstance(episodes, Sequence):
        episodes = (episodes,)
    validated_episodes = tuple(validate_episode(ep) for ep in episodes)
    return validated_episodes


class EpisodeMeta(BaseModel):
    length: int
    msg: str = ""


class EpisodeResponse(BaseModel):
    meta: EpisodeMeta
    episodes: list[EpisodeWith]

    @classmethod
    async def from_episodesnew(cls, episodes: Sequence[EpisodeBase], msg="") -> EpisodeResponse:
        logger.debug("Episodes-in-db Response NEEEEEEEEEEEEEWWWWWWWWWWWWW")
        if not any([msg, episodes]):
            msg = "No Episodes Found"

        valid = []
        async for ep in repack_validatenew(episodes):
            ep_type = type(ep)
            logger.debug(f"ep_type: {ep_type}")
            valid.append(ep_type.model_validate(ep))

        meta_data = EpisodeMeta(
            length=len(valid),
            # calling_func=inspect.stack()[1][3],
            msg=msg,
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))

    @classmethod
    async def from_episodes_async(cls, episodes: AsyncGenerator[EP_OR_BASE_VAR, None], msg="") -> EpisodeResponse:
        logger.debug("Episodes-in-db Response NEEEEEEEEEEEEEWWWWWWWWWWWWW")
        if not any([msg, episodes]):
            msg = "No Episodes Found"

        valid = [ep async for ep in repack_validate_async(episodes)]
        #
        # ep_type = type(ep)
        # logger.debug(f"ep_type: {ep_type}")
        # valid.append(ep_type.model_validate(ep))

        meta_data = EpisodeMeta(
            length=len(valid),
            # calling_func=inspect.stack()[1][3],
            msg=msg,
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))

    def __str__(self):
        return f"{self.__class__.__name__}: {self.meta.length} {self.episodes[0].__class__.__name__}s"

    @classmethod
    async def emptynew(cls, msg: str = "No Episodes Found"):
        return await cls.from_episodesnew([], msg=msg)

    # @classmethod
    # def from_episodes(cls, episodes: EP_FIN_TYP | Sequence[EP_FIN_TYP], msg="") -> EpisodeResponse:
    #     logger.debug("Episodes-in-db Response")
    #     if not any([msg, episodes]):
    #         msg = "No Episodes Found"
    #
    #     valid = [EpisodeWith.model_validate(_) for _ in episodes]
    #
    #     meta_data = EpisodeMeta(
    #         length=len(valid),
    #         msg=msg,
    #     )
    #     return cls.model_validate(dict(episodes=valid, meta=meta_data))

    # @classmethod
    # def empty(cls, msg: str = "No Episodes Found"):
    #     return cls.from_episodes([], msg=msg)


class EpisodeResponseNoDB(EpisodeResponse):
    episodes: list[EpisodeBase]

    @classmethod
    async def from_episodesnew(cls, episodes: Sequence[EpisodeBase], msg="") -> EpisodeResponse:
        if not any([msg, episodes]):
            msg = "No Episodes Found"

        valid = []
        async for ep in repack_validatenew(episodes):
            valid.append(EpisodeBase.model_validate(ep))
        meta_data = EpisodeMeta(
            length=len(valid),
            # calling_func=inspect.stack()[1][3],
            msg=msg,
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))

    # @classmethod
    # def from_episodes(cls, episodes: Sequence[EpisodeBase], msg="") -> EpisodeResponse:
    #     if not any([msg, episodes]):
    #         msg = "No Episodes Found"
    #     episodes = repack_validate(episodes)
    #     valid = [EpisodeBase.model_validate(_) for _ in episodes]
    #     meta_data = EpisodeMeta(
    #         length=len(valid),
    #         # calling_func=inspect.stack()[1][3],
    #         msg=msg,
    #     )
    #     return cls.model_validate(dict(episodes=valid, meta=meta_data))
