import json
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import NEWEPS_JSON
from gurupod.fastguru.database import create_db_and_tables, engine
from gurupod.fastguru.episode_routes import put, router
from gurupod.models.episode import EpisodeIn


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    # await populate_from_json()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/eps")


async def populate_from_json():
    with open(NEWEPS_JSON, 'r') as f:
        eps = json.load(f)
        eps_o = []
        for ep in eps:
            date = datetime.strptime(ep.pop('date'), '%Y-%m-%d')
            ep_o = EpisodeIn(date=date, **ep)
            eps_o.append(ep_o)

        with Session(engine) as session:
            await put(eps_o, session)
