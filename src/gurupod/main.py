from pathlib import Path

from data.consts import EPISODES_HTML
from gurupod.episodes import new_episodes_
from gurupod.reddit import edit_reddit_wiki
from gurupod.writer import HtmlWriter


def main():
    episodes = new_episodes_()

    # writer = RedditWriter(episodes)
    # writer.save_markdown(outfile=Path(EPISODES_MD), markup=markdown)


    writer = HtmlWriter(episodes)
    markdown = writer.all_eps_to_md()
    writer.save_markdown(outfile=Path(EPISODES_HTML), markup=markdown)

    # edit_reddit_wiki(markdown)


if __name__ == "__main__":
    main()
