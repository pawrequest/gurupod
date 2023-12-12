from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Sequence

from gurupod.models.episode import Episode
from gurupod.writer.writer_funcs_leg.html_writer import _html_markup_funcs
from gurupod.writer.writer_funcs_leg.reddit_writer import _reddit_markup_funcs
from gurupod.writer.writer_funcs_leg.wiki_writer import _wiki_markup_funcs


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


ep_markup_wiki = partial(_episodes_markup, markup_funcs=_wiki_markup_funcs)
ep_markup_reddit = partial(_episodes_markup, markup_funcs=_reddit_markup_funcs)
ep_markup_html = partial(_episodes_markup, markup_funcs=_html_markup_funcs)
