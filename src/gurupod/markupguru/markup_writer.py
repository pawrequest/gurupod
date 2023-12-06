from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from legacy.episode_old2 import Episode

def episodes_markup(eps:list, markup_funcs:dict) -> str:
    text = markup_funcs['head_text'](eps)
    for ep in eps:
        text += episode_markup_one(ep, markup_funcs)
    text += markup_funcs['tail_text']()
    return text

def episode_markup_one(episode:Episode, markup_funcs_):
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

