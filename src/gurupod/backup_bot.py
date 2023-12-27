import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select

from data.consts import BACKUP_JSON, DEBUG
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode
from gurupod.models.guru import Guru
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink, RedditThreadGuruLink
from gurupod.models.reddit_thread import RedditThread

logger = get_logger()

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


def db_from_json(session: Session, json_path: Path):
    if not json_path.exists():
        logger.warning(f"Could not find {json_path}")
        return
    # logger.info(f"Loading database from {json_path}\n{[_ for _ in model_to_json_map.keys()]}")
    added = 0
    with open(json_path, "r") as f:
        backup_j = json.load(f)

    for json_name, model_class in model_to_json_map.items():
        for model_dict in backup_j.get(json_name):
            data = json.loads(model_dict)
            model_instance = model_class.model_validate(data)
            try:
                if session.get(model_class, model_instance.id):
                    if DEBUG:
                        logger.debug(f"Skipping {model_instance} as it already exists in the database")
                    continue

            except AttributeError:
                if session.query(model_class).filter_by(**model_instance.dict()).first():
                    if DEBUG:
                        logger.debug(f"Skipping {model_instance} as it already exists in the database")
                    continue

            if DEBUG:
                logger.debug(f"Adding {model_instance} to the session")

            session.add(model_instance)
            added += 1

    if session.new:
        logger.info(f"Adding {added} items from json")
        session.commit()


def get_dated_filename(path: Path):
    date_str = datetime.now().strftime("%Y-%m-%d")
    return path.with_suffix(f".{date_str}.json")


async def backup_bot(session, interval=24 * 60 * 60, backup_filename=None):
    """Continuously backup the database to json with today's date every interval seconds, default = daily"""
    backup_filename = backup_filename or BACKUP_JSON
    while True:
        await asyncio.sleep(interval)
        logger.debug("Waking backup bot")
        await db_to_json(session, get_dated_filename(backup_filename))
        logger.debug(f"Backup bot sleeping for {interval} seconds")
