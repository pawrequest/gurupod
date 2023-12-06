from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import REDDIT_SUB_KEY
from gurupod.fastguru.database import engine, get_session
from gurupod.fastguru.ep_funcs import add_validate_ep, commit_new, filter_existing
from gurupod.models.episode_new import Episode, EpisodeCreate, EpisodeRead
from gurupod.redditguru.reddit import submit_episiode

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






async def _ep_in(ep: EpisodeCreate, session: Session = Depends(get_session)):
    if all([ep.notes, ep.links, ep.date]):
        epi = ep
    else:
        epi = await Episode.ep_scraped(ep.name, ep.url)
    return epi





@router.post("/put/", response_model=List[EpisodeRead])
async def put(episodes: list[EpisodeCreate], session: Session = Depends(get_session)):
    unique_eps = await filter_existing(episodes, session)
    if not unique_eps:
        return []
    episodes_o = [await _ep_in(ep, session) for ep in unique_eps]
    validated = [Episode.model_validate(episode) for episode in episodes_o]
    for ep in validated:
        session.add(ep)
    session.commit()
    [session.refresh(valid) for valid in validated]
    return validated
    # commited = await commit_new(session)

    #
    #
    # new_eps = []
    # for ep in unique_eps:
    #
    #     # if all([ep.get('notes'), ep.get('links'), ep.get('date')]):
    #     if all([ep.notes, ep.links, ep.date]):
    #         # epi = await Episode.ep_loaded(ep, name)
    #         # epi = await Episode.ep_loaded(ep, name)
    #         # epi = await Episode.model_validate(ep)
    #         epi = ep
    #
    #     else:
    #         epi = await Episode.ep_scraped(ep.name, ep.url)
    #
    #     vali = add_validate_ep(epi, session)
    #     new_eps.append(vali)
    #
    # await commit_new(session)
    # return new_eps


# @router.post("/put_scrape/", response_model=EpisodeRead)
# async def put_ep_scrape(episode: EpisodeBase, session: Session = Depends(get_session)):
#     statement = select(Episode).where(Episode.name == episode.name)
#     if exists := session.exec(statement).first():
#         return exists
#
#     try:
#         ep_ = await Episode.ep_scraped(episode.name, episode.url)
#         vali = add_validate_ep(ep_, session)
#         #todo fix returns
#         res = await commit_new(session)
#         return vali
#
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))


@router.get('/new_episode_reddit/{key}/{ep_id}')
async def post_episode_reddit(key, ep_id, session: Session = Depends(get_session)):
    if key != REDDIT_SUB_KEY:
        return 'wrong key'
    episode = session.get(Episode, ep_id)

    return submit_episiode(episode)
