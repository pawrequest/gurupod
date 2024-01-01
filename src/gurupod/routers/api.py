from fastui import AnyComponent, FastUI, components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent
from loguru import logger
from fastapi import APIRouter, Depends
from sqlmodel import Session

from gurupod.core.database import get_session
from gurupod.models.guru import Guru

api_router = APIRouter()

#
#
# @api_rout.get("/guru/{guru_id}/", response_model=FastUI, response_model_exclude_none=True)
# def get_guru(guru_id: int, session: Session = Depends(get_session)) -> list[AnyComponent]:
#     logger.info("get_guru")
#     guru = session.get(Guru, guru_id)
#     logger.info(type(guru))
#     return [
#         c.Page(
#             components=[
#                 c.Heading(text=guru.name, level=2),
#                 c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
#                 c.Details(data=guru),
#             ]
#         ),
#     ]
#
#
# @api_rout.get("/guru/", response_model=FastUI, response_model_exclude_none=True)
# def guru_table(session: Session = Depends(get_session)) -> list[AnyComponent]:
#     """
#     Show a table of four users, `/api` is the endpoint the frontend will connect to
#     when a user visits `/` to fetch components to render.
#     """
#     logger.info("guru_table")
#     data = session.query(Guru).all()
#     try:
#         return [
#             c.Page(  # Page provides a basic container for components
#                 components=[
#                     c.Heading(text="Gurus", level=2),  # renders `<h2>Users</h2>`
#                     c.Table(
#                         data=data,
#                         columns=[
#                             DisplayLookup(field="name", on_click=GoToEvent(url="/guru/{id}/")),
#                         ],
#                     ),
#                 ]
#             ),
#         ]
#     except:
#         logger.error("Error in guru_table")
