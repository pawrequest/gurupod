from __future__ import annotations

from typing import Sequence, AsyncGenerator

from sqlmodel import Session, select

from data.consts import MAIN_URL
from gurupod.gurulog import get_logger, log_episodes
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.scrape import scrape_titles_urls

logger = get_logger()


def validate_add(eps: Sequence[EpisodeBase], session: Session, commit=False) -> tuple[Episode, ...]:
    log_episodes(eps, calling_func=validate_add, msg="Validating")
    valid = [Episode.model_validate(_) for _ in eps]
    session.add_all(valid)
    if commit:
        session.commit()
        # [session.refresh(_) for _ in valid]
    return tuple(valid)


def episode_exists(session, episode) -> bool:
    existing_episode = session.exec(
        select(Episode).where((Episode.url == episode.url) & (Episode.title == episode.title))
    ).first()
    if existing_episode:
        logger.debug(f"Episode {episode.title} already exists in db")
    return existing_episode is not None


def remove_existing_episodes(episodes: Sequence[EpisodeBase], session: Session) -> tuple[EpisodeBase, ...]:
    new_eps = tuple(_ for _ in episodes if not episode_exists(session, _))
    return new_eps


def remove_existing(to_filter: Sequence[str], db_field, session: Session) -> tuple[str, ...]:
    if isinstance(to_filter, str):
        to_filter = [to_filter]
    existing_entries = session.query(db_field).filter(db_field.in_(to_filter)).all()
    existing_set = set(entry[0] for entry in existing_entries)
    new_entries = tuple(_ for _ in to_filter if _ not in existing_set)
    return new_entries


async def scrape_and_filter(aio_session, session) -> AsyncGenerator[EpisodeBase, None]:
    dupes = 0
    async for title, url in scrape_titles_urls(main_url=MAIN_URL, aiosession=aio_session):
        eb = EpisodeBase(title=title, url=url)
        if episode_exists(session, eb):
            dupes += 1
            if dupes >= 3:
                logger.debug(f"Found {dupes} existing episodes, stopping")
                break
            continue
        else:
            logger.debug(f"Found new episode: {eb.title}")
            yield eb
