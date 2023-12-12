from __future__ import annotations

from datetime import datetime



def head_text_wiki(episodes):
    return ""


def tail_text_wiki():
    return ""


def title_text_wiki(episode):
    return f'# {episode.name}\n \n[play on captivate.fm]({episode.url})'


def date_text_wiki(date_pub:datetime):
    return f"\n### Published {date_pub:%A %B %d %Y}\n \n"


def notes_text_wiki(show_notes):
    text = f"### Show Notes\n\n{"\n\n".join(show_notes)}\n\n" if show_notes else ""
    return text


def links_text_wiki(show_links):
    return f"### Show Links\n\n{"\n\n".join([f"[{text}]({link})" for text, link in show_links.episodes()])}\n\n"


def ep_tail_wiki():
    return "\n \n --- \n"


_wiki_markup_funcs = {
    'head_text': head_text_wiki,
    'tail_text': tail_text_wiki,
    'title_text': title_text_wiki,
    'date_text': date_text_wiki,
    'notes_text': notes_text_wiki,
    'links_text': links_text_wiki,
    'final_text': ep_tail_wiki,
}







def oldmarkluop(episode):
    markup_text = f"## [{episode.name}]({episode.url})\n \n"
    markup_text += f"***Date Published:*** {episode.date}\n \n"
    # markup_text += f"[Play on Captivate.fm]({show_url})"

    if episode.notes:
        markup_text += "***Show Notes:***\n \n"
        for note in episode.notes:
            markup_text += f"{note}\n \n"

    if episode.links:
        markup_text += "***Show Links:***\n \n"
        for text, link in episode.links.episodes():
            markup_text += f"[{text}]({link}) \n \n"

    markup_text += "\n \n --- \n"
    return markup_text