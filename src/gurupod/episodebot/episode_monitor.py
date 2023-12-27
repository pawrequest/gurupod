import asyncio

from asyncpraw.models import Redditor, Subreddit
from sqlmodel import Session

from data.consts import SUBMIT_EP_TO_SUBREDDIT
from gurupod.gurulog import get_logger
from gurupod.models.responses import EpisodeWith
from gurupod.redditbot.subred_monitor import message_home
from gurupod.redditbot.reddit_funcs import reddit_episode_submitted_msg, submit_episode_subreddit
from gurupod.episodebot.episode_funcs import scrape, put_episodes_db

logger = get_logger()


async def episode_bot(session: Session, subreddit: Subreddit, interval: int, recipient: Redditor | Subreddit) -> None:
    """Schedule episode scraping and processing."""
    while True:
        logger.debug("Waking Episode Scraper")
        await scrape_and_process_new_eps(session, subreddit, recipient)
        logger.debug(f"Sleeping Episode Scraper for {interval} seconds")
        await asyncio.sleep(interval)


async def scrape_and_process_new_eps(session, subreddit, recipient: Redditor | Subreddit) -> None:
    """Scrape, import to db and post episodes to subreddit and message recipient."""
    scraped = scrape(session)
    res = await put_episodes_db(scraped, session)

    if neweps := res.episodes:
        logger.info(f"Found {len(neweps)} new episodes")
        for ep in neweps:
            await process_new_episode(ep, recipient, subreddit)
    else:
        logger.debug("No new episodes found")


async def process_new_episode(ep: EpisodeWith, recipient, subreddit) -> None:
    """Submit episode post to subreddit and message recipient."""
    if SUBMIT_EP_TO_SUBREDDIT:
        logger.warning(
            f"WRITE TO WEB ENABLED:\n\t\t - SUBMITTING EPISODE TO {subreddit.display_name} - \n\t\t - MESSAGING {recipient.name} -"
        )
        submitted = await submit_episode_subreddit(ep, subreddit)
        message_txt = reddit_episode_submitted_msg(submitted, ep)
        await message_home(recipient, message_txt)
    else:
        logger.warning("WRITE TO WEB DISABLED - NOT PROCESSING NEW EPISODE")
