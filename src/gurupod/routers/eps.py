# from __future__ import annotations
from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger

from gurupod.models.guru import Guru
from gurupod.routers.guru import EpisodeGuruFilter
from gurupod.ui.shared import back_link, default_page, object_ui_with_related
from gurupod.core.database import get_session
from gurupod.models.episode import Episode

router = APIRouter()


# FastUI
@router.get("/{ep_id}", response_model=FastUI, response_model_exclude_none=True)
async def episode_view(ep_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    episode_db = session.get(Episode, ep_id)
    episode_db = Episode.model_validate(episode_db)

    return default_page(
        title=episode_db.title,
        components=[
            back_link(),
            episode_db.ui_detail(),
        ],
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def episode_list_view(
    page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)
) -> list[AnyComponent]:
    logger.info("episode_filter")
    episodes = session.query(Episode).all()
    episodes = [Episode.model_validate(_) for _ in episodes]

    page_size = 50
    filter_form_initial = {}
    if guru_name:
        if guru := session.exec(select(Guru).where(Guru.name == guru_name)).first():
            episodes = [ep for ep in episodes if guru in ep.gurus]
            filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}

    return default_page(
        title="Episodes",
        components=[
            guru_filter(filter_form_initial),
            object_ui_with_related(episodes, container=False, col=True),
            # episodes_with_related(episodes, container=True, col=True),
            c.Pagination(page=page, page_size=page_size, total=len(episodes)),
        ],
    )


def guru_filter(filter_form_initial):
    return c.ModelForm(
        model=EpisodeGuruFilter,
        submit_url=".",
        initial=filter_form_initial,
        method="GOTO",
        submit_on_change=True,
        display_mode="inline",
    )
