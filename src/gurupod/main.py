from pathlib import Path

import praw

from data.consts import EPISODES_HTML, EPISODES_MD, REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, \
    REDDIT_REF_TOK, REDIRECT, SUBRED, USER_AGENT, WIKINAME
from gurupod.episodes import get_eps
from gurupod.writer import HtmlWriter, RedditWriter


def main():
    episodes = get_eps()

    # writer = RedditWriter(episodes)
    # writer.save_markdown(outfile=Path(EPISODES_MD), markup=markdown)
    writer = HtmlWriter(episodes)
    markdown = writer.all_eps_to_md()
    writer.save_markdown(outfile=Path(EPISODES_HTML), markup=markdown)

    reddit = get_reddit()
    subreddit = reddit.subreddit(SUBRED)
    wiki = subreddit.wiki[WIKINAME]

    if input(f"overwrite {WIKINAME} Reddit wiki?").lower()[0] == "y":
        wiki.edit(content=markdown)
        print("edited the wiki")


def get_reddit():
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SEC,
                         user_agent=USER_AGENT,
                         redirect_uri=REDIRECT,
                         refresh_token=REDDIT_REF_TOK
                         )
    return reddit


if __name__ == "__main__":
    main()
