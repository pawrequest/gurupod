from __future__ import annotations

from typing import AsyncGenerator, Sequence, Generator

from aiohttp import ClientSession
from sqlmodel import Session, select

from data.consts import DEBUG, MAIN_URL
from gurupod.episodebot.soup_expander import expand_async
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.episodebot.scrape import scrape_titles_urls
from gurupod.models.guru import Guru
from gurupod.models.responses import EpisodeResponse

logger = get_logger()


async def validate_sort_add_commit(eps: AsyncGenerator[EpisodeBase, None], session: Session) -> list[Episode]:
    eps_ = [Episode.model_validate(_) async for _ in eps]
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


async def remove_existing_episodes_async_gen(
    episodes: AsyncGenerator[EpisodeBase, None], session: Session
) -> AsyncGenerator[EpisodeBase, None]:
    """Yields episodes that do not exist in db."""
    async for episode in episodes:
        if not episode_exists(session, episode):
            yield episode


def remove_existing(to_filter: Sequence[str], db_field, session: Session) -> tuple[str, ...]:
    """Returns tuple of strings which do not match the given db-model-field ."""
    if isinstance(to_filter, str):
        to_filter = [to_filter]
    existing_entries = session.query(db_field).filter(db_field.in_(to_filter)).all()
    existing_set = set(entry[0] for entry in existing_entries)
    new_entries = tuple(_ for _ in to_filter if _ not in existing_set)
    return new_entries


async def scrape_and_filter(
    aio_session, session, captivate_homepage=None, max_rtn=None
) -> AsyncGenerator[EpisodeBase, None]:
    """Scrape titles and urls starting from captivate_mainpage, filter out episodes already in db,
    give up if 3 already existing episodes found."""
    captivate_homepage = captivate_homepage or MAIN_URL
    dupes = 0
    async for title, url in scrape_titles_urls(main_url=captivate_homepage, aiosession=aio_session):
        eb = EpisodeBase(title=title, url=url)
        if episode_exists(session, eb):
            dupes += 1
            if dupes >= 3:
                logger.debug(f"{dupes} duplicates found, giving up")
                break
            continue
        else:
            logger.info(f"NEW EPISODE: {eb.title}")
            yield eb


async def put_episodes_db(episodes: AsyncGenerator, session: Session) -> EpisodeResponse:
    """add episodes to db, minimally provide {url = <url>}"""
    filtered = remove_existing_episodes_async_gen(episodes, session)
    expanded = expand_async(filtered)
    if validated := await validate_sort_add_commit(expanded, session):
        logger.debug(f"validated {len(validated)} episodes")
        assigned = tuple(_ for _ in assign_tags(validated, session, Guru))
        logger.debug(f"assigned {len(assigned)} episodes")
        session.commit()
    resp = await EpisodeResponse.from_episodes_seq(validated)
    return resp


async def scrape(session: Session) -> AsyncGenerator[EpisodeBase, None]:
    async with ClientSession() as aio_session:
        async for ep in scrape_and_filter(aio_session, session):
            if DEBUG:
                logger.debug(f"_scraped {ep.title}")
            yield ep


async def has_gurus(model, session: Session):
    return model.gurus


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
