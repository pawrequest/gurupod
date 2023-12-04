from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from gurupod.episode import Episode


class EpisodeWriter(ABC):
    def __init__(self, episodes: [Episode]):
        self.eps = episodes
        self.text = ''

    def all_eps_to_md(self):
        for ep in self.eps:
            self.text += self.ep_to_md(ep)
        return self.text

    def ep_to_md(self, episode: Episode) -> str:
        text = self.title_text(episode.show_name, episode.show_url)
        text += self.date_text(episode.show_date)

        if episode.show_notes:
            text += self.notes_text(episode.show_notes)

        if episode.show_links:
            text += self.links_text(episode.show_links)

        text += self.break_text()

        return text

    def save_markdown(self, outfile: Path, markup: str or None = None):
        markup = markup or self.text
        if not markup:
            print("no text to write")
            return

        if outfile.exists():
            if input(f"overwrite {outfile}?").lower()[0] != "y":
                print("not overwriting - abort")
                return

        with open(outfile, "w", encoding='utf-8') as output:
            output.write(markup)

    @abstractmethod
    def title_text(self, episode_name, show_url):
        raise NotImplementedError

    @abstractmethod
    def date_text(self, date_pub):
        raise NotImplementedError

    @abstractmethod
    def notes_text(self, show_notes):
        raise NotImplementedError

    @abstractmethod
    def links_text(self, show_links):
        raise NotImplementedError

    @abstractmethod
    def break_text(self):
        raise NotImplementedError


class HtmlWriter(EpisodeWriter):
    def title_text(self, episode_name, show_url):
        return f"<h1>{episode_name}</h1>\n<a href='{show_url}'>Play on Captivate.fm</a>\n"

    def date_text(self, date_pub):
        return f"<p>Date Published: {date_pub}</p>\n"

    def notes_text(self, show_notes):
        notes = "<h3>Show Notes:</h3>\n" + "\n".join(
            [f"<p>{note}</p>" for note in show_notes]) + "\n" if show_notes else ""
        return notes

    def links_text(self, show_links):
        links = "<h3>Show Links:</h3>\n" + "\n".join(
            [f"<a href='{link}'>{text}</a><br>" for text, link in
             show_links.items()]) + "\n" if show_links else ""
        return links

    def break_text(self):
        return "<br> <br>"


class RedditWriter(EpisodeWriter):
    def title_text(self, episode_name, show_url):
        return f"## [{episode_name}]({show_url})\n \n"

    def date_text(self, date_pub):
        return f"***Date Published:*** {date_pub}\n \n"

    def notes_text(self, show_notes):
        notes = "***Show Notes:***\n \n" + "\n \n".join(show_notes) + "\n \n" if show_notes else ""
        return notes

    def links_text(self, show_links):
        links = "***Show Links:***\n \n" + "\n \n".join(
            [f"[{text}]({link})" for text, link in show_links.items()]) + "\n \n"
        return links

    def break_text(self):
        return "\n \n --- \n"
