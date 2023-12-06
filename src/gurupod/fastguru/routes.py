import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from data.consts import EPISODES_JSON
from gurupod.fastguru.database import engine, get_session
from gurupod.fastguru.ep_funcs import commit_new, filter_existing, add_validate_ep
from gurupod.models.episode_new import Episode, EpisodeBase, EpisodeCreate, EpisodeRead, ep_loaded, \
    ep_scraped

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
async def put_ep_json(epsdict: EpisodeCreate, session: Session = Depends(get_session)):
    unique_ep_d = await filter_existing(epsdict, session)
    new_eps = []
    for name, ep in unique_ep_d.items():
        if all([ep.get('show_notes'), ep.get('show_links'), ep.get('show_date')]):
            # epi = await ep_loaded(ep, name)
            epi = await Episode.ep_loaded(ep, name)
        else:
            # epi = await ep_scraped(name, ep['show_url'])
            epi = await Episode.ep_scraped(name, ep['show_url'])
        vali = add_validate_ep(epi, session)
        new_eps.append(vali)

    await commit_new(session)
    return new_eps


@router.post("/put_scrape/", response_model=EpisodeRead)
async def put_ep_scrape(episode_data: EpisodeBase, session: Session = Depends(get_session)):
    statement = select(Episode).where(Episode.name == episode_data.name)
    if exists := session.exec(statement).first():
        return exists

    try:
        episode = await Episode.ep_scraped(episode_data.name, episode_data.url, session)
        # episode = await ep_scraped(episode_data.name, episode_data.url)
        vali = add_validate_ep(episode, session)
        res = await commit_new(session)
        return vali

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def populate_from_json():
    with open(EPISODES_JSON, 'r') as f:
        eps = json.load(f)
        with Session(engine) as session:
            await put_ep_json(eps, session)
