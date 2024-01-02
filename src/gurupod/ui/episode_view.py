from __future__ import annotations

from typing import Sequence, TYPE_CHECKING

from fastui import components as c
from fastui.events import GoToEvent

if TYPE_CHECKING:
    from gurupod.models.episode import Episode, EpisodeBase
from gurupod.ui.shared import Col, gurus_column, title_column, Flex, Row


def play_column(episode: EpisodeBase) -> Col:
    res = Col(
        classes=["col-1 text-right"],
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
    ep_links = [
        c.Link(class_name="well", components=[c.Text(text=ep.title)], on_click=GoToEvent(url=ep.slug))
        for ep in episodes
    ]

    # ep_links = join_components_if_multiple(ep_links)
    return Col(classes=["col-3"], components=[Row(components=[_]) for _ in ep_links])


def episode_list_flex(episodes: Sequence[Episode]) -> Flex:
    if not episodes:
        return Flex(components=[c.Text(text="No episodes")])
    rows = []
    for episode in episodes:
        guru_col = gurus_column(episode.gurus)
        title_col = title_column(episode.title, episode.slug)
        play_col = play_column(episode)
        rows.append(Row(components=[guru_col, title_col, play_col]))
    return Flex(components=rows)

    # return Flex(
    #     components=[
    #         [
    #             Row(
    #                 components=[
    #                     Col(components=[gurus_column(episode.gurus)]),
    #                     Col(components=[title_column(episode.title, episode.slug)]),
    #                     Col(components=[play_column(episode)]),
    #                 ]
    #             )
    #             for episode in episodes
    #         ]
    #     ],
    # )
