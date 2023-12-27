import asyncio

from asyncpraw.models import Redditor, Subreddit

from data.consts import WRITE_TO_WEB
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode
from gurupod.models.responses import EpisodeWith
from gurupod.redditbot.subred_monitor import message_home
from gurupod.redditbot.reddit_funcs import reddit_episode_submitted_msg, submit_episode_subreddit
from gurupod.episodebot.episode_funcs import put_episode_db, _scrape

logger = get_logger()


async def episode_bot(session, subreddit, interval, recipient: Redditor | Subreddit) -> None:
    while True:
        logger.debug("Waking")
        await scrape_import_and_post_episode(session, subreddit, recipient)
        logger.info(f"Sleeping for {interval} seconds")
        await asyncio.sleep(interval)


async def scrape_import_and_post_episode(session, subreddit, recipient: Redditor | Subreddit) -> None:
    scraped = _scrape(session)
    res = await put_episode_db(scraped, session)

    if neweps := res.episodes:
        logger.info(f"Found {len(neweps)} new episodes")
        for ep in neweps:
            await process_new_episode(ep, recipient, subreddit)
    else:
        logger.debug("No new episodes found")


async def process_new_episode(ep: EpisodeWith, recipient, subreddit) -> None:
    if WRITE_TO_WEB:
        logger.warning(
            f"WRITE TO WEB ENABLED:\n\t\t - SUBMITTING EPISODE TO {subreddit.display_name} - \n\t\t - MESSAGING {recipient.name} -"
        )
        submitted = await submit_episode_subreddit(ep, subreddit)
        message_txt = reddit_episode_submitted_msg(submitted, ep)
        await message_home(recipient, message_txt)
    else:
        logger.warning("WRITE TO WEB DISABLED - NOT PROCESSING NEW EPISODE")
