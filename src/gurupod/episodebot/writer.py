from __future__ import annotations

from abc import ABC, abstractmethod

from data.consts import EPISODE_PAGE_TITLE
from gurupod.models.episode import EpisodeBase


class EpisodeWriter(ABC):
    def __init__(self, episodes: EpisodeBase | list[EpisodeBase]):
        if not isinstance(episodes, list):
            episodes = [episodes]
        self.episodes = episodes

    def write_many(self, eps=None) -> str:
        eps = eps or self.episodes
        text = self._post_head_text(eps)
        text += "".join([self.write_one(ep) for ep in eps])
        text += self._post_tail_text()
        return text

    def write_one(self, episode: EpisodeBase) -> str:
        text = self._title_text(episode)
        text += self._date_text(episode.date.date().strftime("%A %B %d %Y"))
        text += self._notes_text(episode.notes) or ""
        text += self._links_text(episode.links) or ""
        return text

    @abstractmethod
    def _post_head_text(self, episode) -> str:
        raise NotImplementedError

    @abstractmethod
    def _title_text(self, episode) -> str:
        raise NotImplementedError

    @abstractmethod
    def _date_text(self, date_pub) -> str:
        raise NotImplementedError

    @abstractmethod
    def _notes_text(self, notes) -> str:
        raise NotImplementedError

    @abstractmethod
    def _links_text(self, links) -> str:
        raise NotImplementedError

    @abstractmethod
    def _ep_tail_text(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _post_tail_text(self) -> str:
        raise NotImplementedError


class HtmlWriter(EpisodeWriter):
    def _contents(self, eps: list[EpisodeBase] = None) -> str:
        eps = eps or self.episodes
        toc = "<h2>Table of Contents</h2>\n"
        for i, ep in enumerate(eps):
            toc += f"<a href='#ep-{i}'>{ep.title}</a><br>\n"
        return toc

    def _post_head_text(self, episode: EpisodeBase) -> str:
        text = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{EPISODE_PAGE_TITLE}</title>
            </head>
            <body>
            """
        text += self._contents(self.episodes)
        return text

    def _title_text(self, episode: EpisodeBase, ep_id="") -> str:
        return f"<h1 id='ep-{str(ep_id)}'>{episode.title}</h1>\n<a href='{episode.url}'>Play on Captivate.fm</a>\n"

    def _date_text(self, date_pub) -> str:
        return f"<p>Date Published: {date_pub}</p>\n"

    def _notes_text(self, notes) -> str:
        notes = "<h3>Show Notes:</h3>\n" + "\n".join([f"<p>{_}</p>" for _ in notes]) + "\n" if notes else ""
        return notes

    def _links_text(self, links) -> str:
        if links:
            links_html = "\n".join([f'<a href="{link}">{text}</a><br>' for text, link in links.episodes()])
            return f"<h3>Show Links:</h3>\n{links_html}"
        return ""

    def _ep_tail_text(self) -> str:
        return "<br> <br>"

    def _post_tail_text(self) -> str:
        return "\n</body>\n</html>"


class RPostWriter(EpisodeWriter):
    def _post_head_text(self, episode: EpisodeBase) -> str:
        return ""

    def _title_text(self, episode: EpisodeBase) -> str:
        return f"## [{episode.title}]({episode.url})\n \n"

    def _date_text(self, date_pub) -> str:
        return f"***{date_pub}***\n \n"

    def _notes_text(self, notes: list[str]) -> str:
        notes = "***Show Notes:***\n \n" + "\n \n".join(notes) + "\n \n" if notes else ""
        return notes

    def _links_text(self, links: dict[str, str]) -> str:
        links = "***Show Links:***\n \n" + "\n \n".join([f"[{text}]({link})\n" for text, link in links.items()])
        return links

    def _ep_tail_text(self) -> str:
        return "\n \n"

    def _post_tail_text(self) -> str:
        return "\n \n"


class RWikiWriter(EpisodeWriter):
    def _post_head_text(self, episode: EpisodeBase) -> str:
        return ""

    def _title_text(self, episode: EpisodeBase) -> str:
        return f"### [{episode.title}]({episode.url})\n \n"

    def _date_text(self, date_pub) -> str:
        return f"***{date_pub}***\n \n"

    def _notes_text(self, notes: list[str]) -> str:
        notes = "***Notes:***\n \n" + "\n \n".join(notes) + "\n \n" if notes else ""
        return notes

    def _links_text(self, links: dict[str, str]) -> str:
        links = "***Links:***\n \n" + "\n \n".join([f"[{text}]({link})" for text, link in links.items()]) + "\n \n"
        return links

    def _ep_tail_text(self) -> str:
        return "\n \n"

    def _post_tail_text(self) -> str:
        return "\n \n"
