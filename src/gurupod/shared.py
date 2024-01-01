from __future__ import annotations as _annotations

from fastui import AnyComponent, components as c
from fastui.events import GoToEvent


def decodethepage(*components: AnyComponent, title: str | None = None) -> list[AnyComponent]:
    return [
        c.PageTitle(text=f"{title}" if title else "durfault title"),
        c.Navbar(
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
            ],
        ),
        c.Page(
            components=[
                *((c.Heading(text=title),) if title else ()),
                *components,
            ],
        ),
        c.Footer(
            extra_text="extra durfault text",
            links=[
                c.Link(
                    components=[c.Text(text="Github")], on_click=GoToEvent(url="https://github.com/pydantic/FastUI")
                ),
            ],
        ),
    ]


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
