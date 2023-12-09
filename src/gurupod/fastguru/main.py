import json
from contextlib import asynccontextmanager
from datetime import datetime

import aiohttp
from fastapi import FastAPI
from sqlmodel import Session, select

from data.consts import MAIN_URL, NEWEPS_JSON
from gurupod.fastguru.database import create_db_and_tables, engine
from gurupod.fastguru.episode_routes import check_new_eps, put, router
from gurupod.models.episode import EpisodeDB, EpisodeIn
from gurupod.scrape import parse_main_page


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        await populate_from_json(session)
        await check_new_eps(session)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/eps")


async def populate_from_json(session):
    with open(NEWEPS_JSON, 'r') as f:
        eps = json.load(f)
        eps_o = [EpisodeIn.model_validate(_) for _ in eps]
        eps_o = sorted(eps_o, key=lambda x: x.date)
        await put(eps_o, session)


# async def check_new_eps(session):
#     existing = session.exec(select(EpisodeDB.name)).all()
#     async with aiohttp.ClientSession() as aio_session:
#         eps = [EpisodeIn(name=name, url=url) async for name, url in parse_main_page(aio_session, main_url=MAIN_URL, existing_eps=existing)]
#         await put(eps, session)
#
