from __future__ import annotations

from pathlib import Path


def episode_markup_one(episode, markup_funcs_):
    text = markup_funcs_['title_text'](episode)
    text += markup_funcs_['date_text'](episode.show_date)
    if episode.show_notes:
        text += markup_funcs_['notes_text'](episode.show_notes)
    if episode.show_links:
        text += markup_funcs_['links_text'](episode.show_links)
    text += markup_funcs_['final_text']()
    return text


def episode_markup_many_set(eps, markup_funcs):
    text = markup_funcs['head_text'](eps)
    for ep in eps:
        text += episode_markup_one(ep, markup_funcs)
    text += markup_funcs['tail_text']()
    return text

def episode_markup_many_list(eps, markup_funcs):
    text = markup_funcs['head_text'](eps)
    for ep in eps:
        text += episode_markup_one(ep, markup_funcs)
    text += markup_funcs['tail_text']()
    return text


def save_markup(outfile: Path, markup: str):
    if not markup:
        print("no text to write")
        return
    with open(outfile, "w", encoding='utf-8') as output:
        output.write(markup)
