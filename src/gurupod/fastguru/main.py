from contextlib import asynccontextmanager

from fastapi import FastAPI

from gurupod.fastguru.database import create_db_and_tables
from gurupod.fastguru.routes import populate_from_json, router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    await populate_from_json()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/eps")