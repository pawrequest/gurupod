from __future__ import annotations

from typing import Sequence

from sqlmodel import Session, select

from gurupod.gurulog import get_logger
from gurupod.models.episode import EpisodeBase, Episode

logger = get_logger()


def _log_urls(urls: Sequence[str], msg: str = None):
    if msg:
        logger.info(msg)
    logger.info("\n".join(["\t" + _ for _ in urls[:5]]))
    if len(urls) > 5:
        logger.info(" ... more ...")


def log_existing_urls(urls: Sequence[str]):
    _log_urls(urls, msg=f"Found {len(urls)} existing episode links in DB:")


def log_new_urls(urls: Sequence[str]):
    _log_urls(urls, msg=f"Found {len(urls)} new episode links:")


def validate_add(eps: Sequence[EpisodeBase], session: Session, commit=False) -> tuple[Episode, ...]:
    valid = [Episode.model_validate(_) for _ in eps]
    session.add_all(valid)
    if commit:
        session.commit()
        [session.refresh(_) for _ in valid]
    return tuple(valid)


def remove_existing_episodes(episodes: Sequence[EpisodeBase], session: Session) -> tuple[EpisodeBase, ...]:
    new_urls = remove_existing_urls([_.url for _ in episodes], session)
    new_eps = tuple(_ for _ in episodes if _.url in new_urls)
    return new_eps


def remove_existing_urls(urls: Sequence[str], session: Session) -> tuple[str, ...]:
    urls_in_db = session.exec(select(Episode.url)).all()
    new_urls = tuple(_ for _ in urls if _ not in urls_in_db)
    log_new_urls(new_urls)
    return new_urls


def remove_existing_smth(to_filter: Sequence[str], db_field, session: Session) -> tuple[str, ...]:
    db_entries = session.exec(select(db_field)).all()
    new_entries = tuple(_ for _ in to_filter if _ not in db_entries)
    return new_entries
