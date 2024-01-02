from fastui import AnyComponent, FastUI, components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger

from gurupod.models.reddit_thread import RedditThread, RedditThreadFE
from gurupod.models.guru import Guru
from gurupod.routers.guru import ThreadGuruFilter
from gurupod.ui.reddit_view import thread_page_flex, thread_detail
from gurupod.ui.shared import decodethepage
from gurupod.core.database import get_session

router = APIRouter()


# FastUI
@router.get("/{thread_id}", response_model=FastUI, response_model_exclude_none=True)
async def thread_view(thread_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    thread = session.get(RedditThread, thread_id)
    if not isinstance(thread, RedditThread):
        pass

    return decodethepage(
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        thread_detail(thread),
        title=thread.title,
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def thread_list_view(
    page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)
) -> list[AnyComponent]:
    try:
        logger.info("thread_filter")
        threads = session.query(RedditThread).all()

        page_size = 50
        filter_form_initial = {}
        if guru_name:
            if guru := session.exec(select(Guru).where(Guru.name == guru_name)).first():
                threads = [thread for thread in threads if guru in thread.gurus]
                filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}

        threads = [RedditThread.model_validate(_) for _ in threads]
        return decodethepage(
            # *tabs(),
            c.ModelForm(
                model=ThreadGuruFilter,
                submit_url=".",
                initial=filter_form_initial,
                method="GOTO",
                submit_on_change=True,
                display_mode="inline",
            ),
            thread_page_flex(threads),
            c.Pagination(page=page, page_size=page_size, total=len(threads)),
            title="Threads",
        )
    except Exception as e:
        logger.error(e)
        raise e
