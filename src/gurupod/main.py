from pathlib import Path

from data.consts import EPISODES_HTML, EPISODES_MD
from gurupod.episodes import new_episodes_
from gurupod.legacy.writer_oop import save_markup
from gurupod.markup_writer import episode_markup_many
from gurupod.markup_reddit import reddit_functions
from gurupod.markup_html import html_functions


def main():
    episodes = new_episodes_()

    # writer = RedditWriter(episodes)
    # writer.save_markdown(outfile=Path(EPISODES_MD), markup=markdown)


    # writer = HtmlWriter(episodes)
    # text = writer.episode_markup_many()
    # save_markup(outfile=Path(EPISODES_HTML), markup=text)

    markup_html = episode_markup_many(episodes, html_functions)
    save_markup(outfile=Path(EPISODES_HTML), markup=markup_html)

    markup_reddit = episode_markup_many(episodes, reddit_functions)
    save_markup(outfile=Path(EPISODES_MD), markup=markup_reddit)

    # edit_reddit_wiki(markdown)


if __name__ == "__main__":
    main()
