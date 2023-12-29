from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Generator, Sequence

from aiohttp import ClientSession
from asyncpraw.models import Redditor, Subreddit, WikiPage
from asyncpraw.reddit import Submission
from sqlmodel import Session, desc, select

from data.consts import DEBUG, EPISODE_MONITOR_SLEEP, MAX_SCRAPED_DUPES, UPDATE_WIKI, WRITE_EP_TO_SUBREDDIT
from gurupod.episode_monitor.soups import MainSoup
from gurupod.core.gurulog import get_logger, log_episodes
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.models.guru import Guru
from gurupod.models.responses import EP_OR_BASE_VAR, EpisodeWith
from gurupod.episode_monitor.writer import RWikiWriter, RPostWriter

logger = get_logger()


class EpisodeBot:
    def __init__(
        self,
        session: Session,
        aio_session: ClientSession,
        subreddit_to_post: Subreddit,
        recipient: Redditor | Subreddit,
        main_soup: MainSoup,
        wiki: WikiPage,
    ):
        self.session = session
        self.aio_session = aio_session
        self.subreddit = subreddit_to_post
        self.recipient = recipient
        self.main_soup = main_soup
        self.wiki = wiki

    async def run(self, sleep_interval: int = EPISODE_MONITOR_SLEEP):
        logger.info(
            f"Scraper | Watching for new episodes: {self.main_soup.main_url} - Posting to http://reddit.com/r/{self.subreddit.display_name}"
        )
        while True:
            logger.debug("Scraper | Waking")
            await self._scrape_and_process_new_eps()
            logger.debug(f"Scraper | Sleeping for {sleep_interval} seconds")
            await asyncio.sleep(sleep_interval)

    async def _scrape_and_process_new_eps(self):
        for ep in await self._scrape():
            await self._process_new_episode(ep)

    async def _scrape(self) -> list[EpisodeWith]:
        episode_stream = self.main_soup.episode_stream(aiosession=self.aio_session)
        new_eps = self._filter_existing_episodes(episode_stream)
        committed = await self._validate_sort_add_commit(new_eps)
        if not committed:
            logger.debug("Scraper | No new episodes found")
            return []
        if gurus_assigned := tuple(_ for _ in self._assign_tags(committed, Guru)):
            self.session.commit()
            logger.info(f"Scraper | assigned {len(gurus_assigned)} episodes")
        log_episodes(committed, self._scrape, "Scraper | Committed")

        resp = [EpisodeWith.model_validate(ep) for ep in committed]
        return resp

    async def _process_new_episode(self, ep: EpisodeWith) -> None:
        if WRITE_EP_TO_SUBREDDIT:
            submitted = await submit_episode_subreddit(ep, self.subreddit)
            logger.warning(
                f"Scraper | Write to web enabled - submitting thread {submitted.shortlink} to r/{self.subreddit.display_name}"
                f" - and sending dm to u/{self.recipient.name}"
            )
            message_txt = reddit_episode_submitted_msg(submitted, ep)
            await message_home(self.recipient, message_txt)
        else:
            logger.warning("Scraper | WRITE TO SUBREDDIT DISABLED - NOT ADDING POST OR MESSAGING")

        if UPDATE_WIKI:
            await self._update_wiki(self.wiki)

    async def _update_wiki(self, wiki_page: WikiPage):
        episodes = self.session.exec(select(Episode).order_by(desc(Episode.date))).all()
        link = f"https://www.reddit.com/r/DecodingTheGurus/wiki/{wiki_page.name}"
        writer = RWikiWriter(episodes)
        markup = writer.write_many()
        await wiki_page.edit(content=markup)
        logger.warning(f"Scraper | WRITE_TO_WIKI is enabled - Updated {link} with {len(episodes)} episodes")

    async def _validate_sort_add_commit(self, eps: AsyncGenerator[EpisodeBase, None]) -> list[Episode]:
        eps_ = [Episode.model_validate(_) async for _ in eps]
        if DEBUG:
            logger.debug(f"Scraper | Validated {len(eps_)} episodes")
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
                if dupes >= MAX_SCRAPED_DUPES:
                    if DEBUG:
                        logger.debug(f"Scraper | {dupes} duplicates found, giving up")
                    break
                continue
            logger.info(f'Scraper | New Episode: "{episode.title}" @ {episode.url}')
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
                logger.info(f"Scraper | Assigned tags {[_.name for _ in title_tags]} to {target.title}")
                yield target


def reddit_episode_submitted_msg(submission, episode: EpisodeWith):
    msg = f"""
    DecodeTheBot discovered a New episode "{episode.title}" on Captivate.fm
    It has been [posted to the test subreddit]({submission.shortlink})


    message u/ProsodySpeaks with thoughts or feedback

    (currently sent from my personal account because the bot is shaddowbanned already lol)
    """
    return msg


async def message_home(recipient: Redditor | Subreddit, msg):
    recip_name = recipient.name if isinstance(recipient, Redditor) else recipient.display_name
    try:
        await recipient.message(subject="New Episode Posted", message=msg)
        logger.info(f"\tMonitor | Sent dm to u/{recip_name}")
    except Exception as e:
        logger.error(f'Monitor | Error sending dm to user or subreddit "{recip_name}": {e}')


async def submit_episode_subreddit(episode: EpisodeBase, sub_reddit: Subreddit) -> Submission:
    try:
        title = f"NEW EPISODE: {episode.title}"
        writer = RPostWriter(episode)
        text = writer.write_many()
        submission: Submission = await sub_reddit.submit(title, selftext=text)
        logger.info(f"\tMonitor | Submitted {episode.title} to {sub_reddit.display_name}: {submission.shortlink}")

        return submission
    except Exception as e:
        logger.error(f"Monitor | Error submitting episode: {e}")
