from __future__ import annotations

from typing import Sequence, TYPE_CHECKING

from fastui import components as c
from fastui.events import GoToEvent

if TYPE_CHECKING:
    from gurupod.core.consts import HasTitleAndSlug
from gurupod.models.reddit_thread import RedditThread
from gurupod.ui.shared import Col, Flex, Row, gurus_column


def link_from_title_slug(rt: "HasTitleAndSlug") -> c.Link:
    link = c.Link(components=[c.Text(text=rt.title)], on_click=GoToEvent(url=rt.slug))
    return link


def reddit_link_column(rt: "RedditThread") -> Col:
    reddit_link = link_from_title_slug(rt)
    return Col(components=[reddit_link])


def reddit_list_row(rts: list["RedditThread"]) -> list[Row]:
    # reddit_links = [link_from_title_slug(_) for _ in reddit_threads]
    return [Row(components=[reddit_link_column(_)]) for _ in rts]


def thread_col(rts: Sequence[RedditThread]) -> Col:
    rows = []
    for rt in rts:
        rows.append(Row(components=[link_from_title_slug(rt)]))
    return Col(components=rows)


def thread_detail(rt: RedditThread) -> Flex:
    return Flex(
        components=[
            Row(
                components=[
                    c.Link(
                        components=[c.Text(text="reddit")],
                        on_click=GoToEvent(url=rt.shortlink),
                    )
                ]
            ),
            c.Paragraph(text=rt.submission.get("selftext")),
        ]
    )


#
def thread_page_flex(rts: Sequence[RedditThread]) -> Flex:
    if not rts:
        return Flex(components=[c.Text(text="No episodes")])
    rows = []
    for rt in rts:
        red_col = reddit_link_column(rt)
        guru_col = gurus_column(rt.gurus)
        rows.append(Row(classes=["container-fluid", "my-2", "py-2", "border"], components=[red_col, guru_col]))
    return Flex(components=rows)
