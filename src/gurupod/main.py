from pathlib import Path

import praw

from data.consts import MAIN_URL, OUTPUT_FILE, REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, \
    REDDIT_REF_TOK, REDIRECT, SUBRED, USER_AGENT, WIKINAME
from data.dld import EXISTING_EPS
from gurupod.episode import get_all_episodes
from gurupod.writer import RedditWriter


def main():
    eps = get_all_episodes(MAIN_URL, existing_eps=EXISTING_EPS)
    writer = RedditWriter(eps)
    markdown = writer.all_eps_to_md()
    writer.save_markdown(outfile=Path(OUTPUT_FILE), markup=markdown)

    reddit = get_reddit()
    subreddit = reddit.subreddit(SUBRED)
    wiki = subreddit.wiki[WIKINAME]

    if input(f"overwrite {WIKINAME}?").lower()[0] == "y":
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
