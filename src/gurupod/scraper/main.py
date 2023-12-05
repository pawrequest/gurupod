from pathlib import Path

from data.consts import EPISODES_MD
from gurupod.models.episode import fetch_episodes
from gurupod.scraper.markup_reddit import reddit_functions
from gurupod.scraper.markup_writer import episode_markup_many_list, save_markup
from gurupod.scraper.reddit import edit_reddit_wiki


def main():
    episodes = fetch_episodes()


    # markup_html = episode_markup_many_list(episodes, html_functions)
    # save_markup(outfile=Path(EPISODES_HTML), markup=markup_html)

    markup_reddit = episode_markup_many_list(episodes, reddit_functions)
    save_markup(outfile=Path(EPISODES_MD), markup=markup_reddit)
    edit_reddit_wiki(markup_reddit)
    # edit_reddit_wiki(backup)


if __name__ == "__main__":
    main()
