import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from data.consts import EPISODES_MOD
from gurupod.database import create_db_and_tables, engine_
from gurupod.routing.episode_routes import import_episodes, ep_router
from gurupod.models.episode import Episode
from gurupod.routing.reddit_routes import red_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine_()) as session:
        ...
        # await populate_from_json(session)
        # await fetch(session)
        # [reddit.post_episode(_) for _ in new]
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(ep_router, prefix="/eps")
app.include_router(red_router, prefix="/red")


async def populate_from_json(session: Session):
    with open(EPISODES_MOD, 'r') as f:
        eps_j = json.load(f)
        print(f'\nLoading {len(eps_j)} episodes from {EPISODES_MOD}\n')
        valid = [Episode.model_validate(_) for _ in eps_j]
        added = await import_episodes(valid, session)
        return added

