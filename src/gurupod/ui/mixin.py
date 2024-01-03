from __future__ import annotations

from typing import Protocol, Union

from fastui import components as c

from gurupod.ui.css import ROW
from gurupod.ui.shared import Col, Flex, Row, UI_TYPE, label, object_ui_self_only, play_column, title_column, ui_link


class UIMixin:
    def ui_self_only(self: UI_TYPE) -> Union[c.Div, c.Link]:
        clink = ui_link(label(self), self.slug)
        return Col(components=[clink])

    def ui_with_related(self: UI_TYPE) -> c.Div:
        cols = []
        if hasattr(self, "gurus"):
            cols.append(object_ui_self_only(self.gurus))
        if hasattr(self, "episodes"):
            cols.append(object_ui_self_only(self.episodes))
        else:
            url = getattr(self, "url", getattr(self, "slug", None))
            cols.append(play_column(url))
        if hasattr(self, "reddit_threads"):
            red_col = object_ui_self_only(self.reddit_threads)
            cols.append(red_col)

        col = title_column(label(self), self.slug)
        cols.insert(1, col)
        row = Row(classes=ROW, components=cols)
        return row


class UIElement(Protocol):
    def ui_detail(self) -> Flex:
        ...

    def ui_self_only(self) -> Union[c.Div, c.Link]:
        ...

    def ui_with_related(self) -> c.Div:
        ...
