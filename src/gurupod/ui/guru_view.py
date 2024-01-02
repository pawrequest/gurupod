from typing import Sequence

from fastui import components as c

from gurupod.models.guru import Guru
from gurupod.ui.episode_view import episodes_column
from gurupod.ui.reddit_view import reddit_list_row, thread_col
from gurupod.ui.shared import Col, Flex, Row, name_column


# def gurus_row(self) -> Row:
#     return Row(
#         components=[
#             episodes_column(self.episodes),
#             name_column(self),
#             reddit_list_row(self.reddit_threads),
#             # [link_from_title_slug(_)for _ in self.reddit_threads],
#         ],
#     )


#
def g_list_col(gurus: Sequence[Guru]) -> Col:
    if not gurus:
        return Flex(components=[c.Text(text="---")])
    rows = []
    for guru in gurus:
        ep = episodes_column(guru.episodes)
        name = name_column(guru)
        red = reddit_list_row(guru.reddit_threads)
        rows.append(Row(classes=["container-fluid", "my-2", "py-2", "border"], components=[ep, name, red]))
    return Flex(components=rows)


#
def guru_page_flex(gurus: Sequence[Guru]) -> Flex:
    if not gurus:
        return Flex(components=[c.Text(text="---")])
    rows = []
    for guru in gurus:
        ep = episodes_column(guru.episodes)
        threads = thread_col(guru.reddit_threads)

        rows.append(Row(classes=["container-fluid", "my-2", "py-2", "border"], components=[ep, threads]))

    return Flex(components=rows)
