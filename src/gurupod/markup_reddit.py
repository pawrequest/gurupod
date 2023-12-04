from __future__ import annotations


def head_text_reddit(episodes):
    return ""


def tail_text_reddit():
    return ""


def title_text_reddit(episode):
    return f"## [{episode.show_name}]({episode.show_url})\n \n"


def date_text_reddit(date_pub):
    return f"***Date Published:*** {date_pub}\n \n"


def notes_text_reddit(show_notes):
    return "***Show Notes:***\n \n" + "\n \n".join(show_notes) + "\n \n" if show_notes else ""


def links_text_reddit(show_links):
    return "***Show Links:***\n \n" + "\n \n".join(
        [f"[{text}]({link})" for text, link in show_links.items()]) + "\n \n"


def final_text_reddit():
    return "\n \n --- \n"


reddit_functions = {
    'head_text': head_text_reddit,
    'tail_text': tail_text_reddit,
    'title_text': title_text_reddit,
    'date_text': date_text_reddit,
    'notes_text': notes_text_reddit,
    'links_text': links_text_reddit,
    'final_text': final_text_reddit,
}
