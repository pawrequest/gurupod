from __future__ import annotations

import praw
from praw.models import WikiPage
from praw.reddit import Submission, Subreddit

from data.consts import DTG_SUB, GURUS, REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, \
    REDDIT_REF_TOK, REDIRECT, USER_AGENT, WIKINAME
from gurupod.markupguru.markup_reddit import reddit_functions
from gurupod.markupguru.markup_writer import episode_markup_one


def edit_reddit_wiki(markup, subreddit_name=DTG_SUB, wiki_name=WIKINAME):
    reddit = reddit_()
    subreddit: Subreddit = reddit.subreddit(subreddit_name)
    wiki: WikiPage = subreddit.wiki[wiki_name]
    wiki.edit(content=markup)
    return {
        'subreddit': subreddit_name,
        'wiki': wiki_name,
        'revision_by': wiki.revision_by,
        'revision_date': wiki.revision_date,
        'revision' : wiki.revision_id,
    }


def reddit_():
    return praw.Reddit(client_id=REDDIT_CLIENT_ID,
                       client_secret=REDDIT_CLIENT_SEC,
                       user_agent=USER_AGENT,
                       redirect_uri=REDIRECT,
                       refresh_token=REDDIT_REF_TOK
                       )


def guru_flair():
    reddit = reddit_()
    subreddit = reddit.subreddit(DTG_SUB)

    for submission in subreddit.stream.submissions():
        submission: praw.models.Submission = submission
        print(submission.title)
        if any(guru in submission.title for guru in GURUS):
            print(f'matched: {submission.id}{submission.title}')
            submission.flair.select("f0c29d96-93e4-11ee-bdde-e666ed3aa602", text="Guru")


def post_episode(episode: 'Episode', sub_reddit: str = 'test'):
    reddit = reddit_()
    subreddit = reddit.subreddit(sub_reddit)
    # subreddit = reddit.subreddit(DTG_SUB)
    title = f'NEW EPISODE: {episode.name}'
    text = episode_markup_one(episode, reddit_functions)
    submission: Submission = subreddit.submit(title, selftext=text)
    print(submission.id)
    return submission.selftext


if __name__ == '__main__':
    # guru_flair()
    # submit_episiode()
    ...
