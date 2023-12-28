from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Generator, Sequence

from aiohttp import ClientSession
from asyncpraw.models import Redditor, Subreddit
from sqlmodel import Session, select

from data.consts import DEBUG, MAX_DUPES, WRITE_EP_TO_SUBREDDIT
from gurupod.podcast_monitor.soups import MainSoup
from gurupod.gurulog import get_logger, log_episodes
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.models.guru import Guru
from gurupod.models.responses import EP_OR_BASE_VAR, EpisodeWith
from gurupod.reddit_monitor.subreddit_bot import message_home, submit_episode_subreddit

logger = get_logger()


class EpisodeBot:
    def __init__(
        self,
        session: Session,
        aio_session: ClientSession,
        subreddit: Subreddit,
        sleep: int,
        recipient: Redditor | Subreddit,
        main_soup: MainSoup,
    ):
        self.session = session
        self.aio_session = aio_session
        self.subreddit = subreddit
        self.sleep = sleep
        self.recipient = recipient
        self.main_soup = main_soup

    async def run(self):
        logger.info(f"Episode Scraper Created for {self.main_soup.main_url}")
        while True:
            logger.debug("Waking Episode Scraper")
            await self._scrape_and_process_new_eps()
            logger.debug(f"Sleeping Episode Scraper for {self.sleep} seconds")
            await asyncio.sleep(self.sleep)

    async def _scrape_and_process_new_eps(self):
        if committed := await self._scrape():
            for ep in committed:
                await self._process_new_episode(ep)
        else:
            logger.debug("No new episodes found")

    async def _scrape(self) -> list[EpisodeWith]:
        episode_stream = self.main_soup.episode_stream(aiosession=self.aio_session)
        new_eps = self._filter_existing_episodes(episode_stream)
        committed = await self._validate_sort_add_commit(new_eps)
        if committed is None:
            logger.debug("No new episodes found")
            return []
        if gurus_assigned := tuple(_ for _ in self._assign_tags(committed, Guru)):
            self.session.commit()
            logger.info(f"assigned {len(gurus_assigned)} episodes")
        log_episodes(committed, self._scrape, "Committed")

        resp = [EpisodeWith.model_validate(ep) for ep in committed]
        return resp

    async def _process_new_episode(self, ep: EpisodeWith) -> None:
        if WRITE_EP_TO_SUBREDDIT:
            logger.warning(
                f"WRITE TO WEB ENABLED:\n\t\t - SUBMITTING EPISODE TO {self.subreddit.display_name} - \n\t\t - MESSAGING {self.recipient.name} -"
            )
            submitted = await submit_episode_subreddit(ep, self.subreddit)
            message_txt = reddit_episode_submitted_msg(submitted, ep)
            await message_home(self.recipient, message_txt)
        else:
            logger.warning("WRITE TO SUBREDDIT DISABLED - NOT ADDING POST OR MESSAGING")

    async def _validate_sort_add_commit(self, eps: AsyncGenerator[EpisodeBase, None]) -> list[Episode]:
        eps_ = [Episode.model_validate(_) async for _ in eps]
        if DEBUG:
            logger.debug(f"Validated in VALIDATE SORT {len(eps_)} episodes")
        sorted_eps = sorted(eps_, key=lambda x: x.date)
        self.session.add_all(sorted_eps)
        self.session.commit()
        [self.session.refresh(_) for _ in sorted_eps]
        return sorted_eps

    async def _filter_existing_episodes(
        self, episodes: AsyncGenerator[EP_OR_BASE_VAR, None]
    ) -> AsyncGenerator[EP_OR_BASE_VAR, None]:
        """Yields episodes that do not exist in db."""
        dupes = 0
        async for episode in episodes:
            if self._episode_exists(episode):
                dupes += 1
                if dupes >= MAX_DUPES:
                    if DEBUG:
                        logger.debug(f"{dupes} duplicates found, giving up")
                    break
                continue
            logger.info(f'New Episode: "{episode.title}" @ {episode.url}')
            yield episode

    def _episode_exists(self, episode: EP_OR_BASE_VAR) -> bool:
        """Check if episode matches title and url of existing episode in db."""
        existing_episode = self.session.exec(
            select(Episode).where((Episode.url == episode.url) & (Episode.title == episode.title))
        ).first()

        return existing_episode is not None

    def _assign_tags(self, to_assign: Sequence, tag_model) -> Generator[Episode, None]:
        """Tagmodel has name attr"""
        if not hasattr(tag_model, "name"):
            raise AttributeError(f"tag_model must have name attribute, got {tag_model}")

        tag_models = self.session.exec(select(tag_model)).all()
        for target in to_assign:
            if title_tags := [_ for _ in tag_models if _.name in target.title]:
                target.gurus.extend(title_tags)
                self.session.add(target)
                logger.info(f"Assigned tags {[_.name for _ in title_tags]} to {target.title}")
                yield target


def reddit_episode_submitted_msg(submission, episode: EpisodeWith):
    msg = f"""
    DecodeTheBot discovered a New episode "{episode.title}" on Captivate.fm
    It has been [posted to the test subreddit]({submission.shortlink})


    message u/ProsodySpeaks with thoughts or feedback

    (currently sent from my personal account because the bot is shaddowbanned already lol)
    """
    return msg
