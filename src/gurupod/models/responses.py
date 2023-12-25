from __future__ import annotations

from typing import List, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel

from gurupod.gurulog import get_logger, log_episodes
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


EP_FIN_TYP = Union[EpisodeRead, Episode, EpisodeWith]
EP_TYP = Union[EpisodeBase, EP_FIN_TYP]
EP_FIN_VAR = TypeVar("EP_FIN_VAR", bound=EP_FIN_TYP)
EP_VAR = TypeVar("EP_VAR", bound=EP_TYP)


def validate_episode(episode):
    try:
        return EpisodeRead.model_validate(episode)
    except Exception as e:
        try:
            return Episode.model_validate(episode)
        except Exception:
            raise ValueError(f"episodes must be {EP_TYP} or Sequence-of, not {type(episode)}")


def repack_validate(episodes: EP_VAR | Sequence[EP_VAR]) -> tuple[EP_VAR, ...]:
    """Takes episode or sequence, checks type, returns tuple of episodes."""

    if not isinstance(episodes, Sequence):
        episodes = (episodes,)

    # log_episodes(episodes, msg="Repacked, now Validating episodes:")

    validated_episodes = tuple(validate_episode(ep) for ep in episodes)
    return validated_episodes


class EpisodeMeta(BaseModel):
    length: int
    msg: str = ""


class EpisodeResponse(BaseModel):
    meta: EpisodeMeta
    episodes: list[EpisodeWith]

    @classmethod
    def from_episodes(cls, episodes: EP_FIN_TYP | Sequence[EP_FIN_TYP], msg="") -> EpisodeResponse:
        logger.debug("Response from_episodes")
        if not any([msg, episodes]):
            msg = "No Episodes Found"
        valid = [EpisodeWith.model_validate(_) for _ in episodes]
        meta_data = EpisodeMeta(
            length=len(valid),
            msg=msg,
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))

    @classmethod
    def empty(cls, msg: str = "No Episodes Found"):
        return cls.from_episodes([], msg=msg)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.meta.length} {self.episodes[0].__class__.__name__}s"


class EpisodeResponseNoDB(EpisodeResponse):
    episodes: list[EpisodeBase]

    @classmethod
    def from_episodes(cls, episodes: Sequence[EpisodeBase], msg="") -> EpisodeResponse:
        if not any([msg, episodes]):
            msg = "No Episodes Found"
        episodes = repack_validate(episodes)
        valid = [EpisodeBase.model_validate(_) for _ in episodes]
        meta_data = EpisodeMeta(
            length=len(valid),
            # calling_func=inspect.stack()[1][3],
            msg=msg,
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))
