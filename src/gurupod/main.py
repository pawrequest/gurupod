import asyncio
import time
from pathlib import Path

import praw

from data.consts import EPISODES_MD, MAIN_URL, REDDIT_CLIENT_ID, REDDIT_CLIENT_SEC, \
    REDDIT_REF_TOK, REDIRECT, SUBRED, USER_AGENT, WIKINAME
from data.dld import EXISTING_EPS
from gurupod.episodes import get_new_eps_as, get_eps
from gurupod.episode_sync import get_all_episodes
from gurupod.writer import RedditWriter


def time_diff():
    st1 = time.perf_counter_ns()
    eps2 = asyncio.run(get_new_eps_as(MAIN_URL, existing_eps=EXISTING_EPS))
    st2 = time.perf_counter_ns()
    eps = get_all_episodes(MAIN_URL, existing_eps=EXISTING_EPS)
    st3 = time.perf_counter_ns()
    time_as = st2 - st1
    time_norm = st3 - st2
    print(f" \n {time_norm=}, {time_as=} ratio = {time_norm / time_as}")


def main():
    # time_diff()
    episodes = get_eps()

    writer = RedditWriter(episodes)
    markdown = writer.all_eps_to_md()
    writer.save_markdown(outfile=Path(EPISODES_MD), markup=markdown)

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
