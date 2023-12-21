from __future__ import annotations

from asyncpraw.models import WikiPage
from asyncpraw.reddit import Submission, Subreddit

from gurupod.models.episode import Episode
from gurupod.writer import RPostWriter


async def edit_reddit_wiki(markup, wiki: WikiPage):
    await wiki.edit(content=markup)
    res = {
        "wiki": wiki.__str__,
        "revision_by": str(wiki.revision_by),
        "revision_date": wiki.revision_date,
        "revision": wiki.revision_id,
    }
    return res


async def submit_episode_subreddit(episode: Episode, sub_reddit: Subreddit):
    title = f"NEW EPISODE: {episode.name}"
    writer = RPostWriter([episode])
    text = writer.write_many()
    submission: Submission = await sub_reddit.submit(title, selftext=text)
    return submission
