from __future__ import annotations, annotations as _annotations

from typing import List, Protocol, Sequence, TYPE_CHECKING, TypeVar, Union

from fastui import AnyComponent, components as c
from fastui.events import BackEvent, GoToEvent
from loguru import logger

from gurupod.ui.css import NAME_COL, PLAY_COL, TITLE_COL

if TYPE_CHECKING:
    from gurupod.models.guru import Guru


class UIElement(Protocol):
    def ui_detail(self) -> Flex:
        ...

    def ui_self_only(self, col=True) -> Union[c.Div, c.Link]:
        ...

    def ui_with_related(self) -> c.Div:
        ...


def object_ui_self_only(master: Sequence[UIElement], col=False, container=False) -> c.Div | list[c.Div]:
    if not master:
        return empty_div(col, container)
    rows = [_.ui_self_only() for _ in master]
    if col:
        rows = Col(components=rows)
    if container:
        rows = Flex(components=rows)
    return rows


def object_ui_with_related(master: Sequence[UIElement], col=False, container=False) -> c.Div | list[c.Div]:
    try:
        rows = [_.ui_with_related() for _ in master]
        rows = [c.Div.model_validate(_) for _ in rows]
        if col:
            rows = Col(components=rows)
            rows = c.Div.model_validate(rows)
        if container:
            rows = Flex(components=rows)
            rows = c.Div.model_validate(rows)
        return rows
    except Exception as e:
        logger.error(e)


def default_page(components: list[AnyComponent], title: str | None = None) -> list[AnyComponent]:
    try:
        return [
            c.PageTitle(text=title if title else "durfault title"),
            nav_bar(),
            c.Page(
                components=[
                    c.Heading(text=title) if title else (),
                    *components,
                ],
            ),
            footer(),
        ]
    except Exception as e:
        logger.error(e)


def empty_page() -> list[AnyComponent]:
    return [
        c.PageTitle(text="durfault title"),
        nav_bar(),
        c.Page(
            components=[
                c.Heading(text="durfault title"),
                c.Text(text="---"),
            ],
        ),
        footer(),
    ]


def Flex(components: List[AnyComponent], classes: list = None) -> c.Div:
    logger.info("Flex")
    try:
        if not components:
            return c.Div(components=[c.Text(text="---")])
    except Exception as e:
        logger.error(e)
    try:
        components = [c.Div.model_validate(_) for _ in components]
        classes = classes or []
        class_name = " ".join(classes)
        class_name = f"container border-bottom border-secondary {class_name}"
        # class_name = f"d-flex border-bottom border-secondary {class_name}"
        return c.Div(components=components, class_name=class_name)
    except Exception as e:
        logger.error(e)


def Row(components: List[AnyComponent], classes: list = None) -> c.Div:
    if not components:
        return c.Div(components=[c.Text(text="---")])
    classes = classes or []
    bs_classes = " ".join(classes)
    bs_classes = f"row {bs_classes}"
    return c.Div(components=components, class_name=bs_classes)


def Col(components: List[AnyComponent], classes: list = None) -> c.Div:
    try:
        classes = classes or []
        bs_classes = " ".join(classes)
        bs_classes = f"col {bs_classes}"
        return c.Div(components=components, class_name=bs_classes)
    except Exception as e:
        logger.error(e)


def ui_link(title, url, on_click=None) -> c.Link:
    on_click = on_click or GoToEvent(url=url)
    link = c.Link(components=[c.Text(text=title)], on_click=on_click)
    return link


def name_column(guru: Guru) -> c.Div:
    return Col(
        classes=NAME_COL,
        components=[
            ui_link(guru.name, guru.slug),
        ],
    )


def title_column(title, url) -> Col:
    return Col(
        classes=TITLE_COL,
        components=[
            ui_link(title, url),
        ],
    )


def play_column(url) -> Col:
    res = Col(
        classes=PLAY_COL,
        components=[
            c.Link(
                components=[c.Text(text="Play")],
                on_click=GoToEvent(url=url),
            ),
        ],
    )
    return res


def empty_div(col, container):
    if col:
        return empty_col()
    elif container:
        return empty_container()


def empty_col():
    return Col(components=[c.Text(text="---")])


def empty_container():
    return Flex(components=[c.Text(text="---")])


def back_link():
    return c.Link(components=[c.Text(text="Back")], on_click=BackEvent())


def fast_ui_default(*components: AnyComponent, title: str | None = None) -> list[AnyComponent]:
    return [
        c.PageTitle(text=f"{title}" if title else "durfault title"),
        nav_bar(),
        c.Page(
            components=[
                *((c.Heading(text=title),) if title else ()),
                *components,
            ],
        ),
        footer(),
    ]


def footer():
    return c.Footer(
        extra_text="extra durfault text",
        links=[
            c.Link(components=[c.Text(text="Github")], on_click=GoToEvent(url="https://github.com/pydantic/FastUI")),
        ],
    )


def nav_bar():
    return c.Navbar(
        title="DecodeTheBot",
        title_event=GoToEvent(url="/"),
        links=[
            c.Link(
                components=[c.Text(text="Episodes")],
                on_click=GoToEvent(url="/eps/"),
                active="startswith:/eps",
            ),
            c.Link(
                components=[c.Text(text="Threads")],
                on_click=GoToEvent(url="/red/"),
                active="startswith:/red",
            ),
            c.Link(
                components=[c.Text(text="Gurus")],
                on_click=GoToEvent(url="/guru/"),
                active="startswith:/guru",
            ),
        ],
    )


def tabs() -> list[AnyComponent]:
    return [
        c.LinkList(
            links=[
                c.Link(
                    components=[c.Text(text="Cities")],
                    on_click=GoToEvent(url="/table/cities"),
                    active="startswith:/table/cities",
                ),
                c.Link(
                    components=[c.Text(text="Users")],
                    on_click=GoToEvent(url="/table/users"),
                    active="startswith:/table/users",
                ),
            ],
            mode="tabs",
            class_name="+ mb-4",
        ),
    ]
