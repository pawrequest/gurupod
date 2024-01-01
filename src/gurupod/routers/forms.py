from __future__ import annotations as _annotations

import enum
from collections import defaultdict
from datetime import date
from typing import Annotated, Literal, TypeAlias

from loguru import logger
from fastapi import APIRouter, Depends, UploadFile
from fastui import AnyComponent, FastUI, components as c
from fastui.events import GoToEvent, PageEvent
from fastui.forms import FormFile, SelectSearchResponse, fastui_form
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator
from pydantic_core import PydanticCustomError
from sqlmodel import Session, desc, select

from gurupod.core.database import get_session
from gurupod.models.episode import Episode
from gurupod.models.guru import Guru
from gurupod.shared import demo_page

router = APIRouter()


@router.get("/search", response_model=SelectSearchResponse)
async def search_view(q: str, session: Session = Depends(get_session)) -> SelectSearchResponse:
    gurus = session.query(Guru).all()
    gurus = [guru for guru in gurus if guru.episodes]
    gurus = sorted(gurus, key=lambda x: len(x.episodes), reverse=True)

    if q:
        gurus = [guru for guru in gurus if q in guru.name]
    # else:
    #     gurus = gurus[0:20]
    guru_d = defaultdict(list)
    for guru in gurus:
        guru_d["gurus"].append({"value": guru.name, "label": f"{guru.name} - {len(guru.episodes)} Episodes"})

    options = [{"label": k, "options": v} for k, v in guru_d.items()]
    print(f"options: {options}")
    # options = [{'label': 'episodes', 'options': [[{'value': ep.model_dump(), 'label': ep.title}] for ep in episodes]}]
    return SelectSearchResponse(options=options)


#
FormKind: TypeAlias = Literal["login", "select", "big"]


class LoginForm(BaseModel):
    email: EmailStr = Field(title="Email Address", description="Try 'x@y' to trigger server side validation")
    password: SecretStr


@router.post("/login", response_model=FastUI, response_model_exclude_none=True)
async def login_form_post(form: Annotated[LoginForm, fastui_form(LoginForm)]):
    print(form)
    return [c.FireEvent(event=GoToEvent(url="/"))]


class ToolEnum(str, enum.Enum):
    hammer = "hammer"
    screwdriver = "screwdriver"
    saw = "saw"
    claw_hammer = "claw_hammer"


class SelectForm(BaseModel):
    select_single: ToolEnum = Field(title="Select Single")
    select_multiple: list[ToolEnum] = Field(title="Select Multiple")
    search_select_single: str = Field(json_schema_extra={"search_url": "/api/forms/search"})
    search_select_multiple: list[str] = Field(json_schema_extra={"search_url": "/api/forms/search"})


class SelectGuru(BaseModel):
    search_select_multiple: list[str] = Field(json_schema_extra={"search_url": "/api/forms/search"})


@router.post("/select", response_model=FastUI, response_model_exclude_none=True)
async def select_form_post(form: Annotated[SelectGuru, fastui_form(SelectGuru)]):
    print(form)
    return [c.FireEvent(event=GoToEvent(url="/"))]


#
# @router.post('/select', response_model=FastUI, response_model_exclude_none=True)
# async def select_form_post(form: Annotated[SelectForm, fastui_form(SelectForm)]):
#     # print(form)
#     return [c.FireEvent(event=GoToEvent(url='/'))]
