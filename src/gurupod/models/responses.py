from __future__ import annotations

from typing import List, Optional, Sequence, TypeVar, Union

from pydantic import BaseModel

from gurupod.models.episode import Episode, EpisodeBase, EpisodeRead
from gurupod.models.guru import GuruBase, GuruRead
from gurupod.models.reddit_model import RedditThreadBase, RedditThreadRead

EP_FIN_TYP = Union[EpisodeRead, Episode]
EP_TYP = Union[EpisodeBase, EP_FIN_TYP]
EP_FIN_VAR = TypeVar("EP_FIN_VAR", bound=EP_FIN_TYP)
EP_VAR = TypeVar("EP_VAR", bound=EP_TYP)


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


def _repack_episodes(episodes: EP_VAR | Sequence[EP_VAR]) -> tuple[EP_VAR]:
    if not isinstance(episodes, Sequence):
        if not isinstance(episodes, EP_TYP):
            try:
                episodes = (EpisodeBase.model_validate(episodes),)
            except Exception:
                # todo better catch
                raise ValueError(f"episodes must be {EP_TYP} or Sequence-of, not {type(episodes)}")

        episodes = (episodes,)

    if not all(isinstance(_, EP_TYP) for _ in episodes):
        try:
            episodes = tuple(EpisodeBase.model_validate(_) for _ in episodes)
        except Exception:
            # todo better catch
            raise ValueError(f"episodes must be {EP_TYP} or Sequence-of, not {type(episodes)}")
    return episodes


## type-specific variants needed?

# def repack_episode_dbs(episodes: EpisodeDB | Sequence[EpisodeDB]) -> tuple[EpisodeDB]:
#     return _repack_episodes(episodes)


# def repack_episodes(episodes: Episode | Sequence[Episode]) -> tuple[Episode]:
#     return _repack_episodes(episodes)

#
# def repack_episodes_out(episodes: EpisodeOut | Sequence[EpisodeOut]) -> tuple[EpisodeOut]:
#     return _repack_episodes(episodes)


class EpisodeMeta(BaseModel):
    length: int
    msg: str = ""


class EpisodeResponse(BaseModel):
    meta: EpisodeMeta
    episodes: list[EpisodeWith]

    class Config:
        populate_by_name = True

    @classmethod
    def from_episodes(cls, episodes: EP_FIN_TYP | Sequence[EP_FIN_TYP], msg="") -> EpisodeResponse:
        if not any([msg, episodes]):
            msg = "No Episodes Found"
        repacked = _repack_episodes(episodes)
        valid = [EpisodeWith.model_validate(_) for _ in repacked]
        meta_data = EpisodeMeta(
            length=len(valid),
            # calling_func=inspect.stack()[1][3],
            msg=msg,
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))

    @classmethod
    def empty(cls, msg: str = "No Episodes Found"):
        meta_data = EpisodeMeta(
            length=0,
            # calling_func=inspect.stack()[1][3],
            msg=msg,
        )
        return cls.model_validate(dict(episodes=[], meta=meta_data))

    def __str__(self):
        return f"{self.__class__.__name__}: {self.meta.length} {self.episodes[0].__class__.__name__}s"


class EpisodeResponseNoDB(EpisodeResponse):
    episodes: list[EpisodeBase]

    @classmethod
    def from_episodes(cls, episodes: Sequence[EpisodeBase], msg="") -> EpisodeResponse:
        if not any([msg, episodes]):
            msg = "No Episodes Found"
        episodes = _repack_episodes(episodes)
        valid = [EpisodeBase.model_validate(_) for _ in episodes]
        meta_data = EpisodeMeta(
            length=len(valid),
            # calling_func=inspect.stack()[1][3],
            msg=msg,
        )
        return cls.model_validate(dict(episodes=valid, meta=meta_data))


#############


# def resp_from_episodes(cls, episodes: EP_VAR | Sequence[EP_VAR], msg="") -> EpisodeResponse:
#     if isinstance(episodes, Sequence):
#         ep_typ = type(episodes[0])
#     else:
#         ep_typ = type(episodes)
#
#     if not any([msg, episodes]):
#         msg = "No Episodes Found"
#     repacked = _repack_episodes(episodes)
#     valid = [ep_typ.model_validate(_) for _ in repacked]
#     meta_data = EpisodeMeta(
#         length=len(valid),
#         # calling_func=inspect.stack()[1][3],
#         msg=msg,
#     )
#     return cls.model_validate(dict(episodes=valid, meta=meta_data))
