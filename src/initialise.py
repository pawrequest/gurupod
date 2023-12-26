import json
from pathlib import Path

from sqlmodel import Session, select

from data.consts import BACKUP_JSON, EPISODES_MOD, EPISODES_OUT, THREADS_JSON
from data.gurunames import GURUS
from gurupod.gurulog import get_logger, log_episodes
from gurupod.models.episode import Episode
from gurupod.models.guru import Guru
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink, RedditThreadGuruLink
from gurupod.models.reddit_model import RedditThread
from gurupod.models.responses import EpisodeWith
from gurupod.routing.episode_funcs import remove_existing
from gurupod.routing.episode_routes import put_episode_db

logger = get_logger()


async def eps_from_file(session: Session) -> list[EpisodeWith]:
    with open(EPISODES_MOD, "r") as f:
        eps_j = json.load(f)
        ep_resp = await put_episode_db(eps_j, session)
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


model_to_json_map = {
    "episodes": Episode,
    "gurus": Guru,
    "reddit_threads": RedditThread,
    "guru_ep_links": GuruEpisodeLink,
    "reddit_thread_episode_links": RedditThreadEpisodeLink,
    "reddit_thread_guru_links": RedditThreadGuruLink,
}


async def db_to_json(session: Session, json_path: Path = BACKUP_JSON):
    backup_json = {}
    for json_name, model_class in model_to_json_map.items():
        results = session.exec(select(model_class)).all()
        backup_json[json_name] = [_.model_dump_json() for _ in results]
        logger.debug(f"Dumped {len(backup_json[json_name])} {json_name} to json")
    with open(json_path, "w") as f:
        json.dump(backup_json, f, indent=4)
    logger.info(f"Saved {len(backup_json)} models to {json_path}")
    return backup_json


# todo crashes oin second run... use validators and serialisers
def db_from_json(session: Session, json_path: Path = BACKUP_JSON):
    logger.info(f"Loading database from {json_path}\n{[_ for _ in model_to_json_map.keys()]}")
    with open(json_path, "r") as f:
        backup_j = json.load(f)

    for json_name, model_class in model_to_json_map.items():
        for model_dict in backup_j.get(json_name):
            data = json.loads(model_dict)
            model_instance = model_class.model_validate(data)
            try:
                if session.get(model_class, model_instance.id):
                    # logger.debug(f"Skipping {model_instance} as it already exists in the database")
                    continue

            except AttributeError:
                if session.query(model_class).filter_by(**model_instance.dict()).first():
                    # logger.debug(f"Skipping {model_instance} as it already exists in the database")
                    continue

            logger.debug(f"Adding {model_instance} to the session")
            session.add(model_instance)

    if session.dirty:
        logger.info(f"Committing {len(session.dirty)} changes to the database")
        session.commit()
