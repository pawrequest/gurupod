from __future__ import annotations

from gurupod.consts import PAGE_TITLE
from gurupod.episodes import Episode


def head_text_html(episodes):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{PAGE_TITLE}</title>
    </head>
    <body>
    {build_table_of_contents(episodes)}
    """


def build_table_of_contents(eps:list[Episode]):
    toc = "<h2>Table of Contents</h2>\n"
    for ep in eps:
        toc += f"<a href='#ep-{ep.num}'>#{ep.num} - {ep.show_name} ({ep.show_date})</a><br>\n"
    return toc


def tail_text_html():
    return "</body>\n</html>"


def title_text_html(episode):
    return f"<h1 id='ep-{episode.num}'>{episode.show_name}</h1>\n<a href='{episode.show_url}'>Play on Captivate.fm</a>\n"


def date_text_html(date_pub):
    return f"<p>Date Published: {date_pub}</p>\n"


def notes_text_html(show_notes):
    return "<h3>Show Notes:</h3>\n" + "\n".join(
        [f"<p>{note}</p>" for note in show_notes]) + "\n" if show_notes else ""


def links_text_html(show_links):
    return "<h3>Show Links:</h3>\n" + "\n".join(
        [f"<a href='{link}'>{text}</a><br>" for text, link in
         show_links.items()]) + "\n" if show_links else ""


def final_text_html():
    return "<br> <br>"


html_functions = {
    'title_text': title_text_html,
    'date_text': date_text_html,
    'notes_text': notes_text_html,
    'links_text': links_text_html,
    'final_text': final_text_html,
    'head_text': head_text_html,
    'tail_text': tail_text_html,
}
