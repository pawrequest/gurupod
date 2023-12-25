import json

from sqlmodel import Session, select

from data.consts import EPISODES_MOD, THREADS_JSON, EPISODES_OUT
from data.gurunames import GURUS
from gurupod.gurulog import log_episodes, get_logger
from gurupod.models.episode import Episode
from gurupod.models.guru import Guru
from gurupod.models.responses import EpisodeWith
from gurupod.routing.episode_funcs import remove_existing
from gurupod.routing.episode_routes import put_ep

logger = get_logger()


async def eps_from_file(session: Session) -> list[EpisodeWith]:
    with open(EPISODES_MOD, "r") as f:
        eps_j = json.load(f)
        ep_resp = await put_ep(eps_j, session)
        if new := ep_resp.episodes:
            logger.debug(f"Loading {len(new)} episodes from {EPISODES_MOD}")
            log_episodes(new, calling_func=eps_from_file, msg=f"Loading from {EPISODES_MOD}")
            return new


async def threads_from_json(session: Session):
    with open(THREADS_JSON, "r") as f:
        threads_j = json.load(f)
        logger.info(f"Loading {len(threads_j)} episodes from {THREADS_JSON}")
        # added_eps = await put_ep(threads_j, session)
    # return added_eps


async def gurus_from_file(session: Session):
    if guru_names := remove_existing(GURUS, Guru.name, session):
        logger.info(f"Adding {len(guru_names)} new gurus: {guru_names}")
        new_gurus = [Guru(name=_) for _ in guru_names]
        session.add_all(new_gurus)
        session.commit()
        [session.refresh(_) for _ in new_gurus]
        return new_gurus


async def episodes_to_json(session: Session):
    episodes = session.exec(select(Episode)).all()
    episodes_j = [_.to_json() for _ in episodes]
    with open(EPISODES_OUT, "w") as f:
        json.dump(episodes_j, f, indent=4)
    logger.info(f"Saved {len(episodes_j)} episodes to {EPISODES_OUT}")
    return episodes_j
