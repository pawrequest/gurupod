from fastui import AnyComponent, FastUI, components as c
from fastui.events import BackEvent
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger
from pydantic import BaseModel, Field

from gurupod.core.database import get_session
from gurupod.models.guru import Guru
from gurupod.ui.guru_view import guru_page_flex
from gurupod.ui.shared import decodethepage

router = APIRouter()


@router.get("/{guru_id}", response_model=FastUI, response_model_exclude_none=True)
async def guru_view(guru_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    guru = session.get(Guru, guru_id)

    return decodethepage(
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Details(data=guru),
        title=guru.name,
    )


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def guru_list_view(
    page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)
) -> list[AnyComponent]:
    logger.info("guru list view")
    gurus = session.query(Guru).all()
    gurus = [_ for _ in gurus if _.episodes or _.reddit_threads]
    gurus.sort(key=lambda x: len(x.episodes) + len(x.reddit_threads), reverse=True)

    page_size = 50
    filter_form_initial = {}
    if guru_name:
        if guru := session.exec(select(Guru).where(Guru.name == guru_name)).first():
            gurus = [guru]
            filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}

    return decodethepage(
        guru_page_flex(gurus),
        c.Pagination(page=page, page_size=page_size, total=len(gurus)),
        title="Gurus",
    )


class EpisodeGuruFilter(BaseModel):
    guru_name: str = Field(
        json_schema_extra={"search_url": "/api/forms/search/episodes/", "placeholder": "Filter by Guru..."}
    )


class ThreadGuruFilter(BaseModel):
    guru_name: str = Field(
        json_schema_extra={"search_url": "/api/forms/search/reddit_threads/", "placeholder": "Filter by Guru..."}
    )
