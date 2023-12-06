from __future__ import annotations

import praw
from praw.models import WikiPage
from praw.reddit import Submission, Subreddit

from data.consts import DTG_SUB, EPISODES_WIKI, GURUS, REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, \
    REDDIT_REF_TOK, REDIRECT, USER_AGENT
from gurupod.markupguru.markup_reddit import reddit_functions
from gurupod.markupguru.markup_writer import episode_markup_one


def edit_reddit_wiki(markup):
    reddit = reddit_()
    subreddit: Subreddit = reddit.subreddit(DTG_SUB)
    wiki: WikiPage = subreddit.wiki[EPISODES_WIKI]
    if input(f"overwrite {EPISODES_WIKI} Reddit wiki?").lower()[0] == "y":
        wiki.edit(content=markup)
        print("edited the wiki")


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


def submit_episiode(episode: 'Episode'):
    reddit = reddit_()
    subreddit = reddit.subreddit('test')
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