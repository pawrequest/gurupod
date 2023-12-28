from __future__ import annotations

from typing import AsyncGenerator, Generator, Sequence

from aiohttp import ClientSession as ClientSession
from sqlmodel import Session, select

from data.consts import MAX_DUPES, DEBUG
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.episodebot.episode_soups import MainSoup
from gurupod.models.guru import Guru
from gurupod.models.responses import EP_OR_BASE_VAR, EpisodeResponse

logger = get_logger()


async def validate_sort_add_commit(eps: AsyncGenerator[EpisodeBase, None], session: Session) -> list[Episode]:
    eps_ = [Episode.model_validate(_) async for _ in eps]
    if DEBUG:
        logger.debug(f"Validated in VALIDATE SORT {len(eps_)} episodes")
    sorted_eps = sorted(eps_, key=lambda x: x.date)
    session.add_all(sorted_eps)
    session.commit()
    [session.refresh(_) for _ in sorted_eps]
    return sorted_eps


def episode_exists(session, episode) -> bool:
    """Check if episode matches title and url of existing episode in db."""
    existing_episode = session.exec(
        select(Episode).where((Episode.url == episode.url) & (Episode.title == episode.title))
    ).first()

    return existing_episode is not None


async def filter_existing_episodes(
    episodes: AsyncGenerator[EP_OR_BASE_VAR, None], session: Session
) -> AsyncGenerator[EP_OR_BASE_VAR, None]:
    """Yields episodes that do not exist in db."""
    dupes = 0
    async for episode in episodes:
        if episode_exists(session, episode):
            dupes += 1
            if dupes >= MAX_DUPES:
                logger.debug(f"{dupes} duplicates found, giving up")
                break
            continue
        logger.info(f"New Episode: {episode.title}")
        yield episode


def remove_existing_str(to_filter: Sequence[str], db_field, session: Session) -> tuple[str, ...]:
    """Returns tuple of strings which do not match the given db-model-field ."""
    if isinstance(to_filter, str):
        to_filter = [to_filter]
    existing_entries = session.query(db_field).filter(db_field.in_(to_filter)).all()
    existing_set = set(entry[0] for entry in existing_entries)
    new_entries = tuple(_ for _ in to_filter if _ not in existing_set)
    return new_entries


async def scrape_and_commit_entry(session: Session, aio_session: ClientSession, main_url) -> EpisodeResponse:
    logger.info(f"Scraping MainPage: {main_url}")
    mainsoup = await MainSoup.from_url(main_url, aio_session)
    episode_stream = mainsoup.episode_stream(aio_session)
    new_eps = filter_existing_episodes(episode_stream, session)
    committed = await validate_sort_add_commit(new_eps, session)
    if assigned := tuple(_ for _ in assign_tags(committed, session, Guru)):
        logger.debug(f"assigned {len(assigned)} episodes")
        session.commit()
    resp = await EpisodeResponse.from_episodes_seq(committed)
    return resp


# async def has_gurus(model, session: Session):
#     return model.gurus


# @warning_log
def assign_tags(to_assign: Sequence, session: Session, tag_model) -> Generator[Episode, None]:
    """Tagmodel has name attr"""
    if not hasattr(tag_model, "name"):
        raise AttributeError(f"tag_model must have name attribute, got {tag_model}")

    tag_models = session.exec(select(tag_model)).all()
    for target in to_assign:
        if title_tags := [_ for _ in tag_models if _.name in target.title]:
            target.gurus.extend(title_tags)
            session.add(target)
            logger.info(f"Assigned tags {title_tags} to {target.title}")
            yield target
