from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Sequence

from sqlmodel import Session, select

from data.consts import BACKUP_JSON, DEBUG
from data.gurunames import GURU_NAMES_SET
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
    for model_name_in_json, model_class in model_to_json_map.items():
        results = session.exec(select(model_class)).all()
        backup_json[model_name_in_json] = [_.model_dump_json() for _ in results]
        logger.debug(f"Dumped {len(backup_json[model_name_in_json])} {model_name_in_json} to {json_path}")
    with open(json_path, "w") as f:
        json.dump(backup_json, f, indent=4)
    logger.info(f"Saved {len(backup_json)} models to {json_path}")
    return backup_json


def db_from_json(session: Session, json_path: Path):
    try:
        with open(json_path, "r") as f:
            backup_j = json.load(f)
    except Exception as e:
        logger.error(f"Error loading json: {e}")
        return

    for json_name, model_class in model_to_json_map.items():
        added = 0
        for one_entry in backup_j.get(json_name):
            one_validated = json.loads(one_entry)
            model_instance = model_class.model_validate(one_validated)

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

            logger.debug(f"Adding {model_instance} to the session")
            session.add(model_instance)
            added += 1
        if added:
            logger.info(f"Loaded {added} {json_name} from {json_path}")

    if session.new:
        session.commit()


def get_dated_filename(path: Path):
    date_str = datetime.now().strftime("%Y-%m-%d")
    return path.with_suffix(f".{date_str}.json")


async def backup_bot(session, interval=24 * 60 * 60, backup_filename=None):
    """Continuously backup the database to json with today's date every interval seconds, default = daily"""
    logger.info(f"Backup bot started, backing up every {interval/60} minutes")
    backup_filename = backup_filename or BACKUP_JSON
    while True:
        await asyncio.sleep(interval)
        logger.debug("Waking backup bot")
        dated_filename = get_dated_filename(backup_filename)
        await db_to_json(session, dated_filename)
        logger.debug(f"Backup bot sleeping for {interval} seconds")


async def gurus_from_file(session: Session):
    if guru_names := remove_existing_str(GURU_NAMES_SET, Guru.name, session):
        logger.info(f"Adding {len(guru_names)} new gurus: {guru_names}")
        new_gurus = [Guru(name=_) for _ in guru_names]
        session.add_all(new_gurus)
        session.commit()
        [session.refresh(_) for _ in new_gurus]
        return new_gurus


def remove_existing_str(to_filter: Sequence[str], db_field, session: Session) -> tuple[str, ...]:
    """Returns tuple of strings which do not match the given db-model-field ."""
    if isinstance(to_filter, str):
        to_filter = [to_filter]
    existing_entries = session.query(db_field).filter(db_field.in_(to_filter)).all()
    existing_set = set(entry[0] for entry in existing_entries)
    new_entries = tuple(_ for _ in to_filter if _ not in existing_set)
    return new_entries