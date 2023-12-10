from __future__ import annotations

from datetime import datetime


# def build_table_of_contents_reddit(eps: list[Episode]):
#     toc = "### GuruPod Episodes:\n \n"
#     for ep in eps:
#         toc += f"{ep.num}: [{ep.show_name}](#{ep.num})\n \n"
#     return toc


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
    return f"### Show Links\n\n{"\n\n".join([f"[{text}]({link})" for text, link in show_links.items()])}\n\n"


def final_text_wiki():
    return "\n \n --- \n"


wiki_markup_funcs = {
    'head_text': head_text_wiki,
    'tail_text': tail_text_wiki,
    'title_text': title_text_wiki,
    'date_text': date_text_wiki,
    'notes_text': notes_text_wiki,
    'links_text': links_text_wiki,
    'final_text': final_text_wiki,
}
