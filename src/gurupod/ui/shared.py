from __future__ import annotations as _annotations

from typing import List, TYPE_CHECKING

from fastui import AnyComponent, components as c
from fastui.events import GoToEvent

from gurupod.models.guru import Guru
from gurupod.ui.css import GURUS_COL, TITLE_COL, NAME_COL

if TYPE_CHECKING:
    pass


def Flex(components: List[AnyComponent], classes: list = None) -> c.Div:
    if not components:
        return c.Div(components=[c.Text(text="---")])
    classes = classes or []
    class_name = " ".join(classes)
    class_name = f"container border-bottom border-secondary {class_name}"
    # class_name = f"d-flex border-bottom border-secondary {class_name}"
    return c.Div(components=components, class_name=class_name)


def Row(components: List[AnyComponent], classes: list = None) -> c.Div:
    if not components:
        return c.Div(components=[c.Text(text="---")])
    classes = classes or []
    bs_classes = " ".join(classes)
    bs_classes = f"row {bs_classes}"
    return c.Div(components=components, class_name=bs_classes)


def Col(components: List[AnyComponent], classes: list = None) -> c.Div:
    classes = classes or []
    bs_classes = " ".join(classes)
    bs_classes = f"col {bs_classes}"
    return c.Div(components=components, class_name=bs_classes)


def decodethepage(*components: AnyComponent, title: str | None = None) -> list[AnyComponent]:
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


def join_components_if_multiple(components: list[AnyComponent]) -> list[AnyComponent]:
    if len(components) < 2:
        return components
    else:
        res = []
        for component in components[:-1]:
            res.extend([component, joining_string()])
        res.append(components[-1])
        return res


def joining_string() -> AnyComponent:
    return c.Text(text=",")


def name_column(guru: Guru) -> Col:
    return Col(
        classes=NAME_COL,
        components=[
            c.Link(
                components=[c.Text(text=guru.name)],
                on_click=GoToEvent(url=guru.slug),
            ),
        ],
    )
    pass


def title_column(title, url) -> Col:
    return Col(
        classes=TITLE_COL,
        components=[
            c.Link(
                components=[c.Text(text=title)],
                on_click=GoToEvent(url=url),
                # class_name="text-primary bg-light",
            ),
        ],
    )


def gurus_column(gurus: list[Guru]) -> Col:
    if not gurus:
        return Col(components=[c.Text(text="---")])
    guru_links = [
        c.Link(class_name="well", components=[c.Text(text=g.name)], on_click=GoToEvent(url=f"/guru/{g.id}"))
        for g in gurus
    ]
    return Col(classes=GURUS_COL, components=[Row(components=[_]) for _ in guru_links])
