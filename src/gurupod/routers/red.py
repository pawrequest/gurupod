from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger

from gurupod.models.reddit_thread import RedditThread
from gurupod.models.guru import Guru
from gurupod.routers.eps import guru_filter
from gurupod.ui.shared import back_link, default_page, object_ui_with_related
from gurupod.core.database import get_session

router = APIRouter()


# FastUI
@router.get("/{thread_id}", response_model=FastUI, response_model_exclude_none=True)
async def thread_view(thread_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    thread = session.get(RedditThread, thread_id)
    thread = RedditThread.model_validate(thread)

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
    page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)
) -> list[AnyComponent]:
    logger.info("thread_filter")
    threads = session.query(RedditThread).all()

    page_size = 50
    filter_form_initial = {}
    if guru_name:
        if guru := session.exec(select(Guru).where(Guru.name == guru_name)).first():
            threads = [thread for thread in threads if guru in thread.gurus]
            filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}

    threads = [RedditThread.model_validate(_) for _ in threads]
    return default_page(
        title="Threads",
        components=[
            guru_filter(filter_form_initial),
            object_ui_with_related(threads, container=False, col=True),
            c.Pagination(page=page, page_size=page_size, total=len(threads)),
        ],
    )
