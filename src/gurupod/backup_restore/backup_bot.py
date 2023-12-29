from __future__ import annotations

import asyncio
import csv
import json
import os
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select

from gurupod.core.consts import BACKUP_JSON, BACKUP_SLEEP, DEBUG, GURU_NAME_LIST_FILE
from gurupod.core.gurulogging import get_logger
from gurupod.models.episode import Episode
from gurupod.models.guru import Guru
from gurupod.models.links import GuruEpisodeLink, RedditThreadEpisodeLink, RedditThreadGuruLink
from gurupod.models.reddit_thread import RedditThread

logger = get_logger()

model_to_json_map = {
    "episode": Episode,
    "guru": Guru,
    "reddit_thread": RedditThread,
    "guru_ep_link": GuruEpisodeLink,
    "reddit_thread_episode_link": RedditThreadEpisodeLink,
    "reddit_thread_guru_link": RedditThreadGuruLink,
}


async def db_to_json(session: Session, json_path: Path = BACKUP_JSON):
    # backup_json = {}
    backup_json = {
        model_name_in_json: [_.model_dump_json() for _ in session.exec(select(model_class)).all()]
        for model_name_in_json, model_class in model_to_json_map.items()
    }

    if not backup_json:
        logger.debug("BackupBot | No models to backup")
        return
    backup_up_model_strs = [f"{len(backup_json[model])} {model}s" for model in backup_json if backup_json[model]]

    logger.info(f"BackupBot | Dumped {', '.join(backup_up_model_strs)} to json")

    if not json_path.exists():
        logger.warning(f"BackupBot | {json_path} does not exist, creating")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.touch()
    with open(json_path, "w") as f:
        json.dump(backup_json, f, indent=4)
    logger.info(f"BackupBot | Saved {sum(len(v)for v in backup_json.values())} models to {json_path}")

    return backup_json


def db_from_json(session: Session, json_path: Path = BACKUP_JSON):
    try:
        with open(json_path, "r") as f:
            backup_j = json.load(f)
    except Exception as e:
        logger.error(f"BackupBot | Error loading json: {e}")
        return

    for json_name, model_class in model_to_json_map.items():
        added = 0
        for json_string in backup_j.get(json_name):
            json_record = json.loads(json_string)
            model_instance = model_class.model_validate(json_record)

            try:
                if session.get(model_class, model_instance.id):
                    if DEBUG:
                        logger.debug(
                            f"BackupBot | Skipping {model_class}: {model_instance.id} as it already exists in the database"
                        )
                    continue

            except AttributeError:
                if session.query(model_class).filter_by(**model_instance.dict()).first():
                    if DEBUG:
                        logger.debug(
                            f"BackupBot | Skipping {model_class} with no id as it already exists in the database"
                        )
                    continue

            session.add(model_instance)
            added += 1
        if added:
            logger.info(f"BackupBot | Loaded {added} {json_name} from {json_path}")

    if session.new:
        session.commit()


def get_dated_filename(path: Path):
    date_str = datetime.now().strftime("%Y-%m-%d")
    return path.with_suffix(f".{date_str}.json")


async def backup_bot(session, interval=BACKUP_SLEEP, backup_filename=BACKUP_JSON):
    """Continuously backup the database to json with today's date every interval seconds, default = daily"""
    logger.info(f"BackupBot | Initialised, backing up every {interval / 60} minutes")
    while True:
        logger.debug("BackupBot | Waking")
        # dated_filename = get_dated_filename(backup_filename)
        await db_to_json(session, backup_filename)
        logger.debug(f"BackupBot | Sleeping for {interval} seconds")
        await asyncio.sleep(interval)


def gurus_from_file(session: Session):
    try:
        guru_names_db = session.exec(select(Guru.name)).all()
        guru_names = set([_ for _ in guru_names_db])
        with open(GURU_NAME_LIST_FILE, "r") as file:
            # reader = csv.reader(file)
            row = file.readline()
            gurus_from_csv = set(name.strip() for name in row.split(","))  # Split by comma and strip whitespace
            # gurus_from_csv = [row for row in reader][0]
        new_gurus = set(gurus_from_csv) - guru_names
        if not new_gurus:
            return
        logger.info(f"BackupBot | Adding {len(new_gurus)} new gurus: {[_ for _ in new_gurus]}")
        gurus = [Guru(name=_) for _ in new_gurus]
        session.add_all(gurus)
        session.commit()
    except Exception as e:
        logger.error(f"BackupBot | Error adding gurus from file: {e}")
        return
