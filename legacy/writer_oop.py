from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from pathlib import Path

if TYPE_CHECKING:
    from gurupod.episodes import Episode


def save_markup(outfile: Path, markup: str):
    if not markup:
        print("no text to write")
        return

    with open(outfile, "w", encoding='utf-8') as output:
        output.write(markup)


class EpisodeWriter(ABC):
    def __init__(self, episodes: [Episode]):
        self.episodes = episodes

    def episode_markup_many(self, eps=None):
        eps = eps or self.episodes
        text = ''
        for ep in eps:
            text += self.episode_markup_one(ep)
        return text

    def episode_markup_one(self, episode: Episode) -> str:
        text = self.title_text(episode)
        text += self.date_text(episode.show_date)

        if episode.show_notes:
            text += self.notes_text(episode.show_notes)

        if episode.show_links:
            text += self.links_text(episode.show_links)

        text += self.final_text()

        return text

    @abstractmethod
    def title_text(self, episode) -> str:
        raise NotImplementedError

    @abstractmethod
    def date_text(self, date_pub) -> str:
        raise NotImplementedError

    @abstractmethod
    def notes_text(self, show_notes) -> str:
        raise NotImplementedError

    @abstractmethod
    def links_text(self, show_links) -> str:
        raise NotImplementedError

    @abstractmethod
    def final_text(self) -> str:
        raise NotImplementedError


HEAD_ = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decoding The Gurus Episodes</title>
</head>
<body>
"""
TAIL = "</body>\n</html>"


class HtmlWriter(EpisodeWriter):
    def episode_markup_many(self, eps=None):
        """ override to add html boilerplate"""
        eps = eps or self.episodes
        self.text = HEAD_
        self.text += self.build_table_of_contents()
        for ep in eps:
            self.text += self.episode_markup_one(ep)
        self.text += TAIL
        return self.text

    def build_table_of_contents(self, eps=None):
        eps = eps or self.episodes
        toc = "<h2>Table of Contents</h2>\n"
        for i, ep in enumerate(eps):
            toc += f"<a href='#ep-{i}'>{ep.show_name}</a><br>\n"
        return toc

    def title_text(self, episode) -> str:
        return f"<h1 id='ep-{episode.num}'>{episode.show_name}</h1>\n<a href='{episode.show_url}'>Play on Captivate.fm</a>\n"

        # return f"<h1>{episode_name}</h1>\n<a href='{show_url}'>Play on Captivate.fm</a>\n"

    # class HtmlWriter(EpisodeWriter):
    #     def all_eps_to_md(self):
    #         """ override to add html boilerplate"""
    #         self.text = HEAD_
    #         for ep in self.eps:
    #             self.text += self.ep_to_md(ep)
    #         self.text += TAIL
    #         return self.text
    #
    #     def title_text(self, episode_name, show_url) -> str:

    def date_text(self, date_pub) -> str:
        return f"<p>Date Published: {date_pub}</p>\n"

    def notes_text(self, show_notes) -> str:
        notes = "<h3>Show Notes:</h3>\n" + "\n".join(
            [f"<p>{note}</p>" for note in show_notes]) + "\n" if show_notes else ""
        return notes

    def links_text(self, show_links) -> str:
        links = "<h3>Show Links:</h3>\n" + "\n".join(
            [f"<a href='{link}'>{text}</a><br>" for text, link in
             show_links.items()]) + "\n" if show_links else ""
        return links

    def final_text(self) -> str:
        return "<br> <br>"


class RedditWriter(EpisodeWriter):
    def title_text(self, episode: Episode):
        return f"## [{episode.show_name}]({episode.show_url})\n \n"

    def date_text(self, date_pub):
        return f"***Date Published:*** {date_pub}\n \n"

    def notes_text(self, show_notes):
        notes = "***Show Notes:***\n \n" + "\n \n".join(show_notes) + "\n \n" if show_notes else ""
        return notes

    def links_text(self, show_links):
        links = "***Show Links:***\n \n" + "\n \n".join(
            [f"[{text}]({link})" for text, link in show_links.items()]) + "\n \n"
        return links

    def final_text(self):
        return "\n \n --- \n"
