from __future__ import annotations

from typing import Sequence

from sqlmodel import Session, select

from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.models.responses import EP_FIN_TYP, EP_VAR

logger = get_logger()


def log_urls(urls: Sequence[str], msg: str = None):
    if not urls:
        return
    if msg:
        logger.info(msg)
        return
    message = "Found urls:\n"
    message += "\n".join("\t" + _ for _ in urls[:5])
    if len(urls) > 5:
        message += " \n\t... more ..."
    logger.info(message)


def log_episodes(eps: Sequence[EP_VAR], msg: str = None):
    if not eps:
        return
    if msg:
        logger.info(msg)
        return
    msg = "Found episodes:\n"
    if isinstance(eps[0], EP_FIN_TYP):
        # msg += '\n'.join("\t" + _.title for _ in eps[:5])
        msg += "\n".join(f"\t {_.date.date()} - {_.title}" for _ in eps[:5])
    elif isinstance(eps[0], EpisodeBase):
        msg += "\n".join("\t" + _.url for _ in eps[:5])
    else:
        raise TypeError(f"Expected {EP_FIN_TYP} or {EpisodeBase}, got {type(eps[0])}")

    if len(eps) > 5:
        msg += " \n\t... more ..."
    logger.info(msg)


def log_existing_urls(urls: Sequence[str]):
    log_urls(urls, msg=f"Found {len(urls)} existing episode links in DB:")


def log_new_urls(urls: Sequence[str]):
    log_urls(urls, msg=f"Found {len(urls)} new episode links:")


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
    if new_urls := tuple(_ for _ in urls if _ not in urls_in_db):
        log_urls(new_urls)
    return new_urls


def remove_existing(to_filter: Sequence[str], db_field, session: Session) -> tuple[str, ...]:
    if isinstance(to_filter, str):
        to_filter = [to_filter]
    db_entries = session.exec(select(db_field)).all()
    new_entries = tuple(_ for _ in to_filter if _ not in db_entries)
    return new_entries
