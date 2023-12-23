from __future__ import annotations

from asyncpraw.models import WikiPage
from asyncpraw.reddit import Submission, Subreddit

from gurupod.models.episode import EpisodeBase
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


async def submit_episode_subreddit(episode: EpisodeBase, sub_reddit: Subreddit):
    title = f"NEW EPISODE: {episode.title}"
    writer = RPostWriter([episode])
    text = writer.write_many()
    submission: Submission = await sub_reddit.submit(title, selftext=text)
    return submission
