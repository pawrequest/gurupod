from fastapi import Depends
from sqlmodel import Session

from data.consts import REDDIT_SUB_KEY
from gurupod.fastguru.database import get_session
from gurupod.fastguru.episode_routes import router
from gurupod.models.episode import EpisodeDB
from gurupod.redditguru.reddit import post_episode


@router.get('/new_episode_reddit/{key}/{ep_id}')
async def post_episode_reddit(key, ep_id, session: Session = Depends(get_session)):
    if key != REDDIT_SUB_KEY:
        return 'wrong key'
    episode = session.get(EpisodeDB, ep_id)

    return post_episode(episode)
