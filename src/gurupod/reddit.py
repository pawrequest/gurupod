import praw
from praw.models import WikiPage
from praw.reddit import Subreddit

from gurupod.data.consts import REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, REDDIT_REF_TOK, REDIRECT, \
    SUBRED, USER_AGENT, \
    WIKINAME


def edit_reddit_wiki(markup):
    reddit = get_reddit()
    subreddit: Subreddit = reddit.subreddit(SUBRED)
    wiki: WikiPage = subreddit.wiki[WIKINAME]
    if input(f"overwrite {WIKINAME} Reddit wiki?").lower()[0] == "y":
        wiki.edit(content=markup)
        print("edited the wiki")


def get_reddit():
    return praw.Reddit(client_id=REDDIT_CLIENT_ID,
                       client_secret=REDDIT_CLIENT_SEC,
                       user_agent=USER_AGENT,
                       redirect_uri=REDIRECT,
                       refresh_token=REDDIT_REF_TOK
                       )
