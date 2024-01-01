from fastui import AnyComponent, FastUI, components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger

from gurupod.models.reddit_thread import RedditThread
from gurupod.models.guru import Guru
from gurupod.routers.gurus import EpisodeGuruFilter, ThreadGuruFilter
from gurupod.shared import demo_page
from gurupod.core.database import get_session
from gurupod.models.episode import Episode

router = APIRouter()


# FastUI
@router.get("/{thread_id}", response_model=FastUI, response_model_exclude_none=True)
async def thread_view(thread_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    thread = session.get(RedditThread, thread_id)

    return demo_page(
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Details(data=thread),
        title=thread.title,
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def thread_list_view(
    page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)
) -> list[AnyComponent]:
    logger.info("thread_filter")
    threads = session.query(RedditThread).all()
    # episodes = [EpisodeWith.model_validate(_) for _ in episodes]

    page_size = 50
    filter_form_initial = {}
    if guru_name:
        if guru := session.exec(select(Guru).where(Guru.name == guru_name)).first():
            threads = [thread for thread in threads if guru in thread.gurus]
            filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}

    return demo_page(
        # *tabs(),
        c.ModelForm(
            model=ThreadGuruFilter,
            submit_url=".",
            initial=filter_form_initial,
            method="GOTO",
            submit_on_change=True,
            display_mode="inline",
        ),
        c.Table(
            data=threads[(page - 1) * page_size : page * page_size],
            data_model=RedditThread,
            columns=[
                DisplayLookup(field="title", on_click=GoToEvent(url="./{id}"), table_width_percent=25),
                # DisplayLookup(field="short_link", on_click=GoToEvent(url="./{id}"), table_width_percent=25),
                # DisplayLookup(field='date', table_width_percent=13),
                # DisplayLookup(field='id', table_width_percent=33),
            ],
        ),
        # c.Link(components=[c.Text(text='Go to Reddit')], on_click=GoToEvent(url=)),
        c.Pagination(page=page, page_size=page_size, total=len(threads)),
        title="Threads",
    )
