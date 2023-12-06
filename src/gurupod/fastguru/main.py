import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import EPISODES_JSON
from gurupod.fastguru.database import create_db_and_tables, engine
from gurupod.fastguru.routes import put_ep_json, router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    await populate_from_json()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/eps")


async def populate_from_json():
    with open(EPISODES_JSON, 'r') as f:
        eps = json.load(f)
        with Session(engine) as session:
            await put_ep_json(eps, session)
