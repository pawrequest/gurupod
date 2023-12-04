from pathlib import Path

from data.consts import EPISODES_HTML, EPISODES_MD
from gurupod.episodes import all_episodes_, all_episodes_set
from gurupod.legacy.writer_oop import save_markup
from gurupod.markup_html import html_functions
from gurupod.markup_reddit import reddit_functions
from gurupod.markup_writer import episode_markup_many_list
from gurupod.reddit import edit_reddit_wiki
from gurupod.data.back import backup


def main():
    episodes = all_episodes_()


    # markup_html = episode_markup_many_list(episodes, html_functions)
    # save_markup(outfile=Path(EPISODES_HTML), markup=markup_html)

    markup_reddit = episode_markup_many_list(episodes, reddit_functions)
    save_markup(outfile=Path(EPISODES_MD), markup=markup_reddit)
    edit_reddit_wiki(markup_reddit)
    # edit_reddit_wiki(backup)


if __name__ == "__main__":
    main()
