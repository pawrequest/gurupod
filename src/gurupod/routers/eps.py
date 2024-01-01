# from __future__ import annotations
from fastui import AnyComponent, FastUI, components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger

from gurupod.models.guru import Guru
from gurupod.models.responses import EpisodeWith
from gurupod.routers.gurus import EpisodeGuruFilter
from gurupod.shared import decodethepage
from gurupod.core.database import get_session
from gurupod.models.episode import Episode, EpisodeRead, EpisodeFE

router = APIRouter()


# FastUI
@router.get("/{ep_id}", response_model=FastUI, response_model_exclude_none=True)
async def episode_view(ep_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    episode_db = session.get(Episode, ep_id)

    return decodethepage(
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Details(data=episode_db),
        title=episode_db.title,
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def episode_list_view(
    page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)
) -> list[AnyComponent]:
    logger.info("episode_filter")
    episodes = session.query(Episode).all()
    episodes = [EpisodeFE.model_validate(_) for _ in episodes]

    page_size = 50
    filter_form_initial = {}
    if guru_name:
        if guru := session.exec(select(Guru).where(Guru.name == guru_name)).first():
            episodes = [ep for ep in episodes if guru in ep.gurus]
            filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}

    return decodethepage(
        # *tabs(),
        c.ModelForm(
            model=EpisodeGuruFilter,
            submit_url=".",
            initial=filter_form_initial,
            method="GOTO",
            submit_on_change=True,
            display_mode="inline",
        ),
        c.Table(
            data=episodes[(page - 1) * page_size : page * page_size],
            data_model=EpisodeFE,
            # columns=[
            #     DisplayLookup(field="title", on_click=GoToEvent(url="./{id}"), table_width_percent=25),
            #     # DisplayLookup(field="gurus", table_width_percent=13),
            #     # DisplayLookup(field='id', table_width_percent=33),
            # ],
        ),
        c.Pagination(page=page, page_size=page_size, total=len(episodes)),
        title="Episodes",
    )
