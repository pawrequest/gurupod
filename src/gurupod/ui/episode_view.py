from __future__ import annotations

from typing import Sequence, TYPE_CHECKING

from fastui import components as c
from fastui.events import GoToEvent

from gurupod.ui.css import ROW, SUB_ROW, PLAY_COL
from gurupod.ui.shared import Col, gurus_column, title_column, Flex, Row

if TYPE_CHECKING:
    from gurupod.models.episode import Episode, EpisodeBase


def play_column(episode: EpisodeBase) -> Col:
    res = Col(
        classes=PLAY_COL,
        components=[
            c.Link(
                components=[c.Text(text="Play")],
                on_click=GoToEvent(url=episode.url),
            ),
        ],
    )
    return res


def episodes_column(episodes: list[Episode]) -> Col:
    if not isinstance(episodes, list):
        episodes = [episodes]
    links = [c.Link(components=[c.Text(text=ep.title)], on_click=GoToEvent(url=ep.slug)) for ep in episodes]
    return Col(components=[Row(classes=SUB_ROW, components=[_]) for _ in links])


def episode_page_flex(episodes: Sequence[Episode]) -> Flex:
    if not episodes:
        return Flex(components=[c.Text(text="No episodes")])
    rows = []
    for episode in episodes:
        guru_col = gurus_column(episode.gurus)
        title_col = title_column(episode.title, episode.slug)
        play_col = play_column(episode)
        rows.append(Row(classes=ROW, components=[guru_col, title_col, play_col]))
    return Flex(components=rows)


def episode_detail_flex(episode: Episode) -> Flex:
    return Flex(
        components=[
            Row(
                components=[
                    c.Link(
                        components=[c.Text(text="Play")],
                        on_click=GoToEvent(url=episode.url),
                    ),
                ]
            ),
            c.Paragraph(text=episode.description),
        ]
    )
