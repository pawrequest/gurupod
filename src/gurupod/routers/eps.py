# from __future__ import annotations
from fastui import AnyComponent, FastUI, components as c
from fastui.events import BackEvent
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger

from gurupod.models.guru import Guru
from gurupod.routers.guru import EpisodeGuruFilter
from gurupod.ui.episode_view import play_column, episode_page_flex
from gurupod.ui.shared import decodethepage, gurus_column, Flex, title_column, Row, Col
from gurupod.core.database import get_session
from gurupod.models.episode import Episode

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

    page_size = 50
    filter_form_initial = {}
    if guru_name:
        if guru := session.exec(select(Guru).where(Guru.name == guru_name)).first():
            episodes = [ep for ep in episodes if guru in ep.gurus]
            filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}

    # episodes = [Episode.model_validate(_) for _ in episodes]
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
        episode_page_flex(episodes),
        c.Pagination(page=page, page_size=page_size, total=len(episodes)),
        title="Episodes",
    )
