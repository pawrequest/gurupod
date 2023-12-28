from __future__ import annotations

import asyncio

from aiohttp import ClientSession
from asyncpraw.models import Redditor, Subreddit
from sqlmodel import Session

from data.consts import WRITE_EP_TO_SUBREDDIT
from gurupod.episodebot.episode_soups import MainSoup
from gurupod.gurulog import get_logger, log_episodes
from gurupod.models.guru import Guru
from gurupod.models.responses import EpisodeWith, EpisodeResponse
from gurupod.redditbot.subred_monitor import message_home
from gurupod.redditbot.reddit_funcs import submit_episode_subreddit
from gurupod.episodebot.episode_funcs import (
    filter_existing_episodes,
    validate_sort_add_commit,
    assign_tags,
)

logger = get_logger()


class EpisodeBot:
    def __init__(
        self, session: Session, aio_session, subreddit: Subreddit, sleep: int, recipient: Redditor | Subreddit, main_url
    ):
        self.session = session
        self.aio_session = aio_session
        self.subreddit = subreddit
        self.sleep = sleep
        self.recipient = recipient
        self.main_url = main_url

    async def wake(self):
        while True:
            logger.debug("Waking Episode Scraper")
            await self._scrape_and_process_new_eps()
            logger.debug(f"Sleeping Episode Scraper for {self.sleep} seconds")
            await asyncio.sleep(self.sleep)

    async def _scrape_and_process_new_eps(self):
        # if committed := await scrape_and_commit_entry(self.session, self.aio_session, self.main_url):
        if committed := await self.scrape_and_commit_entry():
            logger.info(f"Committed {len(committed.episodes)} new episodes to db")
            log_episodes(committed.episodes, self._scrape_and_process_new_eps, "Committed")
            for ep in committed.episodes:
                await self._process_new_episode(ep)
                logger.debug(f"processed {ep.title}")
        else:
            logger.debug("No new episodes found")

    async def _process_new_episode(self, ep: EpisodeWith) -> None:
        if WRITE_EP_TO_SUBREDDIT:
            logger.warning(
                f"WRITE TO WEB ENABLED:\n\t\t - SUBMITTING EPISODE TO {self.subreddit.display_name} - \n\t\t - MESSAGING {self.recipient.name} -"
            )
            submitted = await submit_episode_subreddit(ep, self.subreddit)
            message_txt = reddit_episode_submitted_msg(submitted, ep)
            await message_home(self.recipient, message_txt)
        else:
            logger.warning("WRITE TO WEB DISABLED - NOT PROCESSING NEW EPISODE")

    async def scrape_and_commit_entry(self) -> EpisodeResponse:
        logger.info(f"Scraping MainPage: {self.main_url}")

        mainsoup = await MainSoup.from_url(self.main_url, self.aio_session)

        episode_stream = mainsoup.episode_stream(aiosession=self.aio_session)
        new_eps = filter_existing_episodes(episode_stream, self.session)
        committed = await validate_sort_add_commit(new_eps, self.session)
        if assigned := tuple(_ for _ in assign_tags(committed, self.session, Guru)):
            self.session.commit()
            logger.debug(f"assigned {len(assigned)} episodes")
        resp = await EpisodeResponse.from_episodes_seq(committed)
        logger.info(f"Response received {resp.episodes}")
        return resp


# async def episode_bot(
#     session: Session, aio_session, subreddit: Subreddit, interval: int, recipient: Redditor | Subreddit, main_url=None
# ) -> None:
#     """Schedule episode scraping and processing."""
#     while True:
#         logger.debug("Waking Episode Scraper")
#         await scrape_and_process_new_eps(session, aio_session, subreddit, recipient)
#         logger.debug(f"Sleeping Episode Scraper for {interval} seconds")
#         await asyncio.sleep(interval)

#
# async def scrape_and_process_new_eps(session, aiosession, subreddit, recipient: Redditor | Subreddit, main_url) -> None:
#     """Scrape, import to db and post episodes to subreddit and message recipient."""
#     if committed := await scrape_and_commit_entry(session, aiosession, main_url):
#         logger.info(f"Committed {len(committed.episodes)} new episodes to db")
#         log_episodes(committed.episodes, scrape_and_process_new_eps, "Committed")
#         for ep in committed.episodes:
#             await process_new_episode(ep, recipient, subreddit)
#     else:
#         logger.debug("No new episodes found")


# async def process_new_episode(ep: EpisodeWith, recipient, subreddit) -> None:
#     """Submit episode post to subreddit and message recipient."""
#     if WRITE_EP_TO_SUBREDDIT:
#         logger.warning(
#             f"WRITE TO WEB ENABLED:\n\t\t - SUBMITTING EPISODE TO {subreddit.display_name} - \n\t\t - MESSAGING {recipient.name} -"
#         )
#         submitted = await submit_episode_subreddit(ep, subreddit)
#         message_txt = reddit_episode_submitted_msg(submitted, ep)
#         await message_home(recipient, message_txt)
#     else:
#         logger.warning("WRITE TO WEB DISABLED - NOT PROCESSING NEW EPISODE")
def reddit_episode_submitted_msg(submission, episode: EpisodeWith):
    msg = f"""
    DecodeTheBot discovered a New episode "{episode.title}" on Captivate.fm
    It has been [posted to the test subreddit]({submission.shortlink})


    message u/ProsodySpeaks with thoughts or feedback

    (currently sent from my personal account because the bot is shaddowbanned already lol)
    """
    return msg
