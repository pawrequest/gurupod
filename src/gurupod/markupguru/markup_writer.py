from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Sequence, TYPE_CHECKING

from gurupod.markupguru.markup_html import html_markup_funcs
from gurupod.markupguru.markup_reddit import reddit_markup_funcs
from gurupod.markupguru.wiki_writer import wiki_markup_funcs

if TYPE_CHECKING:
    from gurupod.models.episode import Episode


def _episodes_markup(episodes: Sequence[Episode], markup_funcs: dict) -> str:
    text = markup_funcs['head_text'](episodes)
    for ep in episodes:
        text += _episode_markup_one(ep, markup_funcs)
    text += markup_funcs['tail_text']()
    return text


def _episode_markup_one(episode: Episode, markup_funcs_):
    text = markup_funcs_['title_text'](episode)
    text += markup_funcs_['date_text'](episode.date)
    if episode.notes:
        text += markup_funcs_['notes_text'](episode.notes)
    if episode.links:
        text += markup_funcs_['links_text'](episode.links)
    text += markup_funcs_['final_text']()
    return text


def save_markup(outfile: Path, markup: str):
    if not markup:
        print("no text to write")
        return
    with open(outfile, "w", encoding='utf-8') as output:
        output.write(markup)


episodes_wiki = partial(_episodes_markup, markup_funcs=wiki_markup_funcs)
episodes_reddit = partial(_episodes_markup, markup_funcs=reddit_markup_funcs)
episodes_html = partial(_episodes_markup, markup_funcs=html_markup_funcs)
