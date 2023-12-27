from __future__ import annotations

from asyncpraw.models import WikiPage
from asyncpraw.reddit import Submission, Subreddit

from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode, EpisodeBase
from gurupod.episodebot.writer import RPostWriter
from gurupod.models.responses import EpisodeWith

logger = get_logger()


async def submission_in_stream_by_id(submission_id: str, subreddit: Subreddit) -> bool:
    async for submission in subreddit.stream.submissions():
        if submission_id == submission.id:
            return True


async def title_in_subreddit_stream(title, subreddit: Subreddit) -> bool:
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if title in submission.title:
            return True


async def edit_reddit_wiki(markup: str, wiki: WikiPage):
    await wiki.edit(content=markup)
    res = {
        "wiki": wiki.__str__,
        "revision_by": str(wiki.revision_by),
        "revision_date": wiki.revision_date,
        "revision": wiki.revision_id,
    }
    return res


async def submit_episode_subreddit(episode: EpisodeBase, sub_reddit: Subreddit) -> Submission:
    try:
        title = f"NEW EPISODE: {episode.title}"
        writer = RPostWriter(episode)
        text = writer.write_many()
        submission: Submission = await sub_reddit.submit(title, selftext=text)
        logger.info(f"\n\tSubmitted {episode.title} to {sub_reddit.display_name}: {submission.shortlink}")

        return submission
    except Exception as e:
        logger.error(f"Error submitting episode: {e}")
        return None


def reddit_episode_submitted_msg(submission, episode: EpisodeWith):
    msg = f"""
    DecodeTheBot discovered a New episode "{episode.title}" on Captivate.fm
    It has been [posted to the test subreddit]({submission.shortlink})


    message u/ProsodySpeaks with thoughts or feedback

    (currently sent from my personal account because the bot is shaddowbanned already lol)
    """
    return msg
