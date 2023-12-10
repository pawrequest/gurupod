from typing import List

from aiohttp import ClientSession
from fastapi import APIRouter, Depends
from sqlmodel import Session, desc, select

from data.consts import MAIN_URL
from gurupod.fastguru.database import get_session
from gurupod.models.episode import Episode, EpisodeDB, EpisodeOut
from gurupod.scrape import maybe_expand_episode, scrape_new_eps

router = APIRouter()


@router.get("/{ep_id}", response_model=EpisodeOut)
def read_one(ep_id: int, session: Session = Depends(get_session)):
    return session.get(EpisodeDB, ep_id)


@router.get("/", response_model=List[EpisodeOut])
def read_all(session: Session = Depends(get_session)):
    return session.exec(select(EpisodeDB)).all()


@router.post("/put/", response_model=List[EpisodeOut])
async def put(episodes: list[Episode], session: Session = Depends(get_session)):
    # if new_eps := filter_existing_names(episodes, session):
    if new_eps := filter_existing_url(episodes, session):
        for ep in new_eps:
            await maybe_expand_episode(ep)
        new_eps = sorted(new_eps, key=lambda x: x.date)
        return validate_add(new_eps, session, commit=True)
    return []


@router.get('/fetch', response_model=List[EpisodeOut])
async def fetch_episodes(session: Session = Depends(get_session)):
    """ check captivate for new episodes and add to db"""
    if new_eps := await scrape_eps(session):
        print(f'found {len(new_eps)} new episodes to scrape: \n{"\n".join(_.name for _ in new_eps)}')
        return await put(new_eps, session)
    else:
        print('no new episodes found')
        return []


@router.get('/scrape', response_model=List[EpisodeOut])
async def scrape_eps(session: Session = Depends(get_session)):
    """ endpoint for dry-run / internal use"""
    existing_urls = await existing_urls_(session)
    async with ClientSession() as aio_session:
        return await scrape_new_eps(aio_session, main_url=MAIN_URL, existing_urls=existing_urls)


async def existing_urls_(session: Session) -> list[str]:
    if existing_urls := session.exec(select(EpisodeDB.url).order_by(desc(EpisodeDB.date))).all():
        await log_existing_urls(existing_urls)
        return list(existing_urls)
    return []


async def log_existing_urls(existing_urls):
    print(f'\nFound {len(existing_urls)} existing episode links in DB:')
    print("\n".join(['\t' + _ for _ in existing_urls[:5]]))
    if len(existing_urls) > 5:
        print(' ... more ...')
    print('\n')

def log_new_urls(new_eps):
    print(f'\nFound {len(new_eps)} new episode links:')
    print("\n".join(['\t' + _.url for _ in new_eps[:5]]))
    if len(new_eps) > 5:
        print(' ... more ...')
    print('\n')

def validate_add(eps: list[Episode], session: Session, commit=False) -> List[Episode | EpisodeOut]:
    valid = [EpisodeDB.model_validate(_) for _ in eps]
    if valid:
        session.add_all(valid)
        if commit:
            session.commit()
            [session.refresh(_) for _ in valid]
        return valid
    else:
        return []




def filter_existing_names(eps: list[Episode], session: Session) -> List[Episode]:
    names_in_db = session.exec(select(EpisodeDB.name)).all()
    print(f'found {len(names_in_db)} existing episodes in db')
    new_eps = []
    for ep in eps:
        if ep.name in names_in_db:
            print(f'episode {ep.name} already exists in db')
        else:
            print(f'adding episode {ep.name}')
            new_eps.append(ep)
    return new_eps

def filter_existing_url(eps: list[Episode], session: Session) -> List[Episode]:
    urls_in_db = session.exec(select(EpisodeDB.url)).all()
    new_eps = [_ for _ in eps if _.url not in urls_in_db]
    log_new_urls(new_eps)
    return new_eps

