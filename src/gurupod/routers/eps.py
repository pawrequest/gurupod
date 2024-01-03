# from __future__ import annotations
from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger

from gurupod.core.consts import PAGE_SIZE
from gurupod.models.guru import Guru
from gurupod.routers.guroute import guru_filter
from gurupod.ui.shared import back_link, default_page
from gurupod.ui.mixin import objects_ui_with
from gurupod.core.database import get_session
from gurupod.models.episode import Episode

router = APIRouter()


# FastUI
@router.get("/{ep_id}", response_model=FastUI, response_model_exclude_none=True)
async def episode_view(ep_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    episode = session.get(Episode, ep_id)

    return default_page(
        components=[
            back_link(),
            episode.ui_detail(),
        ],
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def episode_list_view(
    page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)
) -> list[AnyComponent]:
    logger.info("episode_filter")
    data, filter_form_initial = guru_filter_init(guru_name, session, Episode)
    data.sort(key=lambda x: x.date, reverse=True)

    total = len(data)
    data = data[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]

    return default_page(
        title="Episodes",
        components=[
            guru_filter(filter_form_initial, "episodes"),
            objects_ui_with(data),
            c.Pagination(page=page, page_size=PAGE_SIZE, total=total),
        ],
    )


def guru_filter_init(guru_name, session, clazz):
    filter_form_initial = {}
    if guru_name:
        guru = session.exec(select(Guru).where(Guru.name == guru_name)).one()
        # data = guru.episodes
        statement = select(clazz).where(clazz.gurus.any(Guru.id == guru.id))
        data = session.exec(statement).all()
        filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}
    else:
        data = session.query(clazz).all()
    return data, filter_form_initial
