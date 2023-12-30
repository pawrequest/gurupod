from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Sequence

from aiohttp import ClientSession
from asyncpraw.models import Redditor, Subreddit, WikiPage
from asyncpraw.reddit import Reddit, Submission
from sqlmodel import Session, desc, select
from loguru import logger

from gurupod.core.consts import (
    DEBUG,
    DM_ADDRESS,
    EPISODE_MONITOR_SLEEP,
    MAIN_URL,
    MAX_EPISODE_IMPORT,
    MAX_SCRAPED_DUPES,
    SUB_TO_POST,
    SUB_TO_WIKI,
    UPDATE_WIKI,
    WIKI_TO_WRITE,
    WRITE_EP_TO_SUBREDDIT,
)
from gurupod.core.logger_funcs import log_episodes
from gurupod.episode_monitor.soups import MainSoup
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.models.guru import Guru
from gurupod.models.responses import EP_OR_BASE_VAR, EpisodeWith
from gurupod.episode_monitor.writer import RPostWriter, RWikiWriter


async def get_wiki(sub_to_update_wiki):
    """Returns wiki page or optionally creates it if it doesn't exist."""
    try:
        wiki = await sub_to_update_wiki.wiki.get_page(WIKI_TO_WRITE)
        return wiki
    except Exception as e:
        if input(f"Wiki page {WIKI_TO_WRITE} does not exist. Create it? (y/n)").lower() == "y":
            wiki = await sub_to_update_wiki.wiki.create(WIKI_TO_WRITE, "Created by DecodeTheBot")
            logger.warning(f"Created wiki page {WIKI_TO_WRITE}", bot_name="Scraper")
            return wiki
        else:
            logger.error(f"Error getting wiki page: {e}", bot_name="Scraper")


class EpisodeBot:
    def __init__(
        self,
        session: Session,
        aio_session: ClientSession,
        main_soup: MainSoup,
        reddit: Reddit,
        subreddit_to_post: Subreddit,
        recipient: Redditor,
        wiki: WikiPage,
    ):
        self.session = session
        self.aio_session = aio_session
        self.reddit = reddit
        self.main_soup = main_soup
        self.subreddit = subreddit_to_post
        self.recipient = recipient
        self.wiki = wiki

    @classmethod
    async def from_config(cls, session: Session, aio_session: ClientSession, reddit: Reddit) -> EpisodeBot:
        main_soup = await MainSoup.from_url(MAIN_URL, aio_session)
        subreddit_to_post = await reddit.subreddit(SUB_TO_POST)
        sub_to_update_wiki = await reddit.subreddit(SUB_TO_WIKI)
        wiki = await get_wiki(sub_to_update_wiki)
        recipient = await reddit.redditor(DM_ADDRESS, fetch=False)
        return cls(session, aio_session, main_soup, reddit, subreddit_to_post, recipient, wiki)

    async def run(self, sleep_interval: int = EPISODE_MONITOR_SLEEP) -> None:
        """Schedule scraper and writer tasks."""
        logger.info(
            f"Initialised : {self.main_soup.main_url} - Posting to http://reddit.com/r/{self.subreddit.display_name}",
            bot_name="Scraper",
        )
        while True:
            logger.debug("Waking", bot_name="Scraper")
            await self.update_episodes()
            logger.debug(f"Sleeping for {sleep_interval} seconds", bot_name="Scraper")
            await asyncio.sleep(sleep_interval)

    async def update_episodes(self) -> None:
        """Scrape and process new episodes."""
        new_eps = await self._scrape_and_commit()
        if new_eps:
            if not WRITE_EP_TO_SUBREDDIT:
                logger.warning("WRITE_TO_SUBREDDIT is disabled - Not writing to web", bot_name="Scraper")
                return
            if len(new_eps) > MAX_EPISODE_IMPORT:
                logger.warning(
                    f"Found {len(new_eps)} episodes - more than {MAX_EPISODE_IMPORT=} - Not writing to web ",
                    bot_name="Scraper",
                )
                return
        [await self._process_new_episode(ep) for ep in new_eps]

    async def _scrape_and_commit(self) -> list[EpisodeWith]:
        """Scrape new episodes and add to db."""
        episode_stream = self.main_soup.episode_stream(aiosession=self.aio_session)
        new_stream = self._filter_existing_eps(episode_stream)

        existing_gurus = self.session.exec(select(Guru)).all()
        added = [await self._add_assign(ep, existing_gurus) async for ep in new_stream]
        if added:
            self.session.commit()
            log_episodes(added, self._scrape_and_commit, "Committed", bot_name="Scraper")

        return [EpisodeWith.model_validate(ep) for ep in added]

    async def _add_assign(self, ep, existing_gurus) -> Episode:
        """Add episode to session and assign gurus."""
        try:
            val = Episode.model_validate(ep)
            self.session.add(val)
            val = _assign_tags_one(val, existing_gurus)
            self.session.add(val)
            logger.info(f"New Episode: {val.title} @ {ep.url} with {[_.name for _ in val.gurus]}", bot_name="Scraper")
            return val
        except Exception as e:
            logger.error(f"Error adding {val.title} to session: {e}", bot_name="Scraper")
            self.session.rollback()

    async def _process_new_episode(self, ep: EpisodeWith) -> None:
        """Submit episode to subreddit, update wiki and send confirmation dm."""
        submitted = await submit_episode_subreddit(ep, self.subreddit)
        logger.warning(
            f"Scraper | Write to web enabled - submitting thread {submitted.shortlink} to r/{self.subreddit.display_name}"
            f"+ Sending dm to u/{self.recipient.name}"
        )
        message_txt = reddit_episode_submitted_msg(submitted, ep)
        await message_home(self.recipient, message_txt)

        if UPDATE_WIKI:
            await self._update_wiki(self.wiki)

    async def _update_wiki(self, wiki_page: WikiPage):
        """Update wiki page with episodes."""
        episodes = self.session.exec(select(Episode).order_by(desc(Episode.date))).all()
        link = f"https://www.reddit.com/r/{self.subreddit.display_name}/wiki/{wiki_page.name}"
        writer = RWikiWriter(episodes)
        markup = writer.write_many()
        await wiki_page.edit(content=markup)
        logger.warning(f"WRITE_TO_WIKI is enabled - Updated {link} with {len(episodes)} episodes", bot_name="Scraper")

    async def _filter_existing_eps(
        self, episodes: AsyncGenerator[EpisodeBase, None]
    ) -> AsyncGenerator[EpisodeBase, None]:
        """Yields episodes that do not exist in db."""
        dupes = 0
        async for episode in episodes:
            if self._episode_exists(episode):
                dupes += 1
                if dupes >= MAX_SCRAPED_DUPES:
                    if DEBUG:
                        logger.debug(f"{dupes} duplicates found, giving up", bot_name="Scraper")
                    break
                continue
            yield episode

    def _episode_exists(self, episode: EP_OR_BASE_VAR) -> bool:
        """Check if episode matches title and url of existing episode in db."""
        existing_episode = self.session.exec(
            select(Episode).where((Episode.url == episode.url) & (Episode.title == episode.title))
        ).first()

        return existing_episode is not None


def reddit_episode_submitted_msg(submission, episode: EpisodeWith) -> str:
    msg = f"""
    DecodeTheBot discovered a New episode "{episode.title}" on Captivate.fm
    It has been [posted to the test subreddit]({submission.shortlink})


    message u/ProsodySpeaks with thoughts or feedback

    (currently sent from my personal account because the bot is shaddowbanned already lol)
    """
    return msg


async def message_home(recipient: Redditor | Subreddit, msg: str) -> None:
    recip_name = recipient.name if isinstance(recipient, Redditor) else recipient.display_name
    try:
        await recipient.message(subject="New Episode Posted", message=msg)
        logger.info(f"Sent dm to u/{recip_name}", bot_name="\tMonitor")
    except Exception as e:
        logger.error(f'Monitor | Error sending dm to user or subreddit "{recip_name}": {e}')


async def submit_episode_subreddit(episode: EpisodeBase, sub_reddit: Subreddit) -> Submission:
    try:
        title = f"NEW EPISODE: {episode.title}"
        writer = RPostWriter(episode)
        text = writer.write_many()
        submission: Submission = await sub_reddit.submit(title, selftext=text)
        logger.info(
            f"Submitted {episode.title} to {sub_reddit.display_name}: {submission.shortlink}", bot_name="\tMonitor"
        )

        return submission
    except Exception as e:
        logger.error(f"Error submitting episode: {e}", bot_name="Monitor")


def get_matched_strs(episode: Episode, match_strs: set[str]) -> set[str]:
    return {_ for _ in match_strs if _.lower() in episode.title.lower()}


def _assign_tags_one(episode: Episode, gurus: Sequence[Guru]) -> Episode:
    tag_names = set([_.name for _ in gurus])
    matched = get_matched_strs(episode, tag_names)
    matched_gurus = [_ for _ in gurus if _.name in matched]
    episode.gurus.extend(matched_gurus)
    return episode
