from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger

from gurupod.models.reddit_thread import RedditThread
from gurupod.models.guru import Guru
from gurupod.routers.eps import guru_filter
from gurupod.ui.shared import back_link, default_page_new, master_with_related
from gurupod.core.database import get_session

router = APIRouter()


# FastUI
@router.get("/{thread_id}", response_model=FastUI, response_model_exclude_none=True)
async def thread_view(thread_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    thread = session.get(RedditThread, thread_id)
    thread = RedditThread.model_validate(thread)

    if not thread:
        raise Exception(f"Thread {thread_id} not found")
    return default_page_new(
        title=thread.title,
        components=[
            back_link(),
            thread.ui_detail(),
        ],
    )

    #
    # return default_page(
    #     c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
    #     thread.ui_detail(),
    #     title=thread.title,
    # )


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
    return default_page_new(
        title="Threads",
        components=[
            guru_filter(filter_form_initial),
            master_with_related(threads, container=False, col=True),
            # threads_with_related(threads, container=True, col=True),
            c.Pagination(page=page, page_size=page_size, total=len(threads)),
        ],
    )

    # return default_page(
    #     # *tabs(),
    #     c.ModelForm(
    #         model=ThreadGuruFilter,
    #         submit_url=".",
    #         initial=filter_form_initial,
    #         method="GOTO",
    #         submit_on_change=True,
    #         display_mode="inline",
    #     ),
    #     threads_with_related(threads, container=True, col=True),
    #     c.Pagination(page=page, page_size=page_size, total=len(threads)),
    #     title="Threads",
    # )
    # except Exception as e:
    # logger.error(e)
    # raise e
