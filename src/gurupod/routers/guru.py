from fastui import AnyComponent, FastUI, components as c
from fastui.events import BackEvent
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger
from pydantic import BaseModel, Field

from gurupod.core.database import get_session
from gurupod.models.guru import Guru
from gurupod.ui.shared import default_page, object_ui_with_related, back_link, empty_page, log_object_state
from gurupod.models.episode import Episode

router = APIRouter()


@router.get("/{guru_id}", response_model=FastUI, response_model_exclude_none=True)
async def guru_view(guru_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    guru = session.get(Guru, guru_id)
    # guru = Guru.model_validate(guru)
    # guru = Guru.model_validate(guru)
    if not isinstance(guru, Guru):
        return empty_page()

    return default_page(
        title=guru.name,
        components=[
            back_link(),
            guru.ui_detail(),
        ],
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def guru_list_view(page: int = 1, session: Session = Depends(get_session)) -> list[AnyComponent]:
    logger.info("guru list view")
    gurus = session.query(Guru).all()
    gurus = [_ for _ in gurus if _.episodes or _.reddit_threads]
    gurus.sort(key=lambda x: len(x.episodes) + len(x.reddit_threads), reverse=True)
    if not gurus:
        return empty_page()

    try:
        mst = object_ui_with_related(gurus)

        page_size = 50
        return default_page(
            title="Gurus",
            components=[
                mst,
                c.Pagination(page=page, page_size=page_size, total=len(gurus)),
            ],
        )
    except Exception as e:
        logger.error(e)
        return empty_page()


class EpisodeGuruFilter(BaseModel):
    guru_name: str = Field(
        json_schema_extra={"search_url": "/api/forms/search/episodes/", "placeholder": "Filter by Guru..."}
    )


class ThreadGuruFilter(BaseModel):
    guru_name: str = Field(
        json_schema_extra={"search_url": "/api/forms/search/reddit_threads/", "placeholder": "Filter by Guru..."}
    )
