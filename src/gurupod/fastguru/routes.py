import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from data.consts import EPISODES_JSON
from gurupod.fastguru.database import engine, get_session
from gurupod.fastguru.ep_funcs import commit_new, filter_existing, validate_add_ep
from gurupod.models.episode_new import Episode, EpisodeBase, EpisodeRead

router = APIRouter()


@router.get("/all/", response_model=List[EpisodeRead])
def read_episodes():
    with Session(engine) as session:
        episodes = session.exec(select(Episode)).all()
        return episodes


@router.get("/{ep_id}", response_model=EpisodeRead)
def read_one_episode(ep_id: int):
    with Session(engine) as session:
        eppy = session.get(Episode, ep_id)
        return eppy


@router.post("/put_json/", response_model=List[EpisodeRead])
async def put_ep_json(epsdict: dict, session: Session = Depends(get_session)):
    for name, ep in await filter_existing(epsdict, session):
        if all([ep.get('show_notes'), ep.get('show_links'), ep.get('show_date')]):
            # epi = await ep_loaded(ep, name)
            epi = await Episode.ep_loaded(ep, name)
        else:
            # epi = await ep_scraped(name, ep['show_url'], session)
            epi = await Episode.ep_scraped(name, ep['show_url'], session)
        vali = validate_add_ep(epi, session)
    return await commit_new(session)


@router.post("/put_scrape/", response_model=EpisodeRead)
async def put_ep_scrape(episode_data: EpisodeBase, session: Session = Depends(get_session)):
    statement = select(Episode).where(Episode.name == episode_data.name)
    if exists := session.exec(statement).first():
        return exists

    try:
        episode = await Episode.ep_scraped(episode_data.name, episode_data.url, session)
        vali = validate_add_ep(episode, session)
        return await commit_new(session)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def populate_from_json():
    with open(EPISODES_JSON, 'r') as f:
        eps = json.load(f)
        with Session(engine) as session:
            await put_ep_json(eps, session)
