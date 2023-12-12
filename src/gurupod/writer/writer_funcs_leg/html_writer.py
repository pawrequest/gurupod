from __future__ import annotations

from data.consts import EPISODE_PAGE_TITLE
from gurupod.models.episode import Episode, EpisodeDB


def head_text_html(episodes:list[EpisodeDB]):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{EPISODE_PAGE_TITLE}</title>
    </head>
    <body>
    {build_table_of_contents(episodes)}
    """


def build_table_of_contents(eps: list[EpisodeDB]):
    toc = "<h2>Table of Contents</h2>\n"
    for ep in eps:
        toc += f"<a href='#ep-{ep.id}'>#{ep.id} - {ep.name} ({ep.date})</a><br>\n"
    return toc


def tail_text_html():
    return "</body>\n</html>"


def title_text_html(episode: EpisodeDB):
    return f"<h1 id='ep-{episode.id}'>{episode.name}</h1>\n<a href='{episode.url}'>Play on Captivate.fm</a>\n"


def date_text_html(date):
    return f"<p>Date Published: {date}</p>\n"


def notes_text_html(notes):
    return "<h3>Show Notes:</h3>\n" + "\n".join(
        [f"<p>{note}</p>" for note in notes]) + "\n" if notes else ""


def links_text_html(links):
    return "<h3>Show Links:</h3>\n" + "\n".join(
        [f"<a href='{link}'>{text}</a><br>" for text, link in
         links.episodes()]) + "\n" if links else ""


def final_text_html():
    return "<br> <br>"


_html_markup_funcs = {
    'title_text': title_text_html,
    'date_text': date_text_html,
    'notes_text': notes_text_html,
    'links_text': links_text_html,
    'final_text': final_text_html,
    'head_text': head_text_html,
    'tail_text': tail_text_html,
}
