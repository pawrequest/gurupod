from fastui import AnyComponent, FastUI, components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from loguru import logger
from pydantic import BaseModel, Field

from gurupod.core.database import get_session
from gurupod.models.guru import Guru
from gurupod.models.responses import GuruWith
from gurupod.routers.forms import SelectGuru
from gurupod.shared import demo_page
from gurupod.routers.tables import tabs

router = APIRouter()


@router.get("/{guru_id}", response_model=FastUI, response_model_exclude_none=True)
async def guru_view(guru_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
    guru = session.get(Guru, guru_id)

    return demo_page(
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
    # gurus = [GuruWith.model_validate(_) for _ in gurus]

    page_size = 50
    filter_form_initial = {}
    if guru_name:
        if guru := session.exec(select(Guru).where(Guru.name == guru_name)).first():
            gurus = [guru]
            filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}

    return demo_page(
        # *tabs(),
        c.ModelForm(
            model=GuruFilter,
            submit_url=".",
            initial=filter_form_initial,
            method="GOTO",
            submit_on_change=True,
            display_mode="inline",
        ),
        # search_select_single: str = Field(json_schema_extra={'search_url': '/api/forms/search'})
        # c.ModelForm(model=SelectGuru, submit_url='/api/forms/select'),
        c.Table(
            data=gurus[(page - 1) * page_size : page * page_size],
            data_model=Guru,
            columns=[
                DisplayLookup(field="name", on_click=GoToEvent(url="./{id}"), table_width_percent=25),
                # DisplayLookup(field='date', table_width_percent=13),
                # DisplayLookup(field='id', table_width_percent=33),
            ],
        ),
        c.Pagination(page=page, page_size=page_size, total=len(gurus)),
        title="Gurus",
    )


class GuruFilter(BaseModel):
    guru_name: str = Field(json_schema_extra={"search_url": "/api/forms/search", "placeholder": "Filter by Guru..."})
