from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from gurupod.core.consts import PAGE_SIZE
from gurupod.models.reddit_thread import RedditThread
from gurupod.routers.eps import guru_filter_init
from gurupod.routers.guroute import guru_filter
from gurupod.ui.shared import back_link, default_page
from gurupod.ui.mixin import objects_ui_with
from gurupod.core.database import get_session

router = APIRouter()


# FastUI
@router.get("/{thread_id}", response_model=FastUI, response_model_exclude_none=True)
async def thread_view(thread_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    thread = session.get(RedditThread, thread_id)
    if not thread:
        raise Exception(f"Thread {thread_id} not found")
    return default_page(
        title=thread.title,
        components=[
            back_link(),
            thread.ui_detail(),
        ],
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def thread_list_view(
    page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session), data=None
) -> list[AnyComponent]:
    data, filter_form_initial = guru_filter_init(guru_name, session, RedditThread)
    data.sort(key=lambda x: x.created_datetime, reverse=True)

    total = len(data)
    data = data[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]

    return default_page(
        title="Threads",
        components=[
            guru_filter(filter_form_initial, model="reddit_threads"),
            objects_ui_with(data),
            c.Pagination(page=page, page_size=PAGE_SIZE, total=total),
        ],
    )
