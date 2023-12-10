from __future__ import annotations

from typing import TYPE_CHECKING

from asyncpraw.models import WikiPage
from asyncpraw.reddit import Reddit, Submission, Subreddit

from data.consts import DTG_SUB, EPISODES_WIKI, GURU_FLAIR_ID, REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, \
    REDDIT_REF_TOK, REDIRECT, USER_AGENT
from data.gurunames import GURUS
from gurupod.markupguru.markup_writer import episodes_reddit

if TYPE_CHECKING:
    from gurupod.models.episode import Episode


async def reddit_() -> Reddit:
    return Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SEC,
        user_agent=USER_AGENT,
        redirect_uri=REDIRECT,
        refresh_token=REDDIT_REF_TOK
    )


async def subreddit_dflt(reddit: Reddit = None):
    if reddit is None:
        reddit = await reddit_()
    return await reddit.subreddit(DTG_SUB)


async def wiki_page_dflt(subreddit: Subreddit = None):
    if subreddit is None:
        subreddit = subreddit_dflt()
    wiki: WikiPage = await subreddit.wiki.get_page(EPISODES_WIKI)
    return wiki


async def find_title_in_subreddit_stream(title, reddit: Reddit, subreddit_name=DTG_SUB):
    subreddit: Subreddit = reddit.subreddit(subreddit_name)
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if title in submission.title:
            return submission.id


async def guru_flair(subreddit: Subreddit):
    async for submission in await submissions_with_gurus_in_title(subreddit=subreddit, gurus=GURUS):
        submission.flair.select(GURU_FLAIR_ID, text="Guru")


async def submissions_with_gurus_in_title(subreddit: Subreddit, gurus=GURUS) -> Submission:
    async for submission in subreddit.stream.submissions():
        if any(guru in submission.title for guru in gurus):
            yield submission


async def submit_episode_subreddit(episode: Episode, sub_reddit: Subreddit):
    title = f'NEW EPISODE: {episode.name}'
    text = episodes_reddit([episode])[0]
    submission: Submission = await sub_reddit.submit(title, selftext=text)
    return submission.__dict__


async def edit_reddit_wiki(markup, wiki: WikiPage):
    await wiki.edit(content=markup)
    res = {
        'wiki': wiki.__str__,
        'revision_by': str(wiki.revision_by),
        'revision_date': wiki.revision_date,
        'revision': wiki.revision_id,
    }
    return res


if __name__ == '__main__':
    # guru_flair()
    # submit_episiode()
    ...
