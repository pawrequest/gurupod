from fastapi import Depends
from sqlmodel import Session

from data.consts import REDDIT_SUB_KEY
from gurupod.fastguru.database import get_session
from gurupod.fastguru.main import app
from gurupod.models.episode_old import Episode
from gurupod.redditguru.reddit import submit_episiode


@app.get('/new_episode_reddit/{key}/{ep_id}')
async def new_episode_reddit(key, ep_id, session: Session = Depends(get_session)):
    if key != REDDIT_SUB_KEY:
        return 'wrong key'
    episode = session.get(Episode, ep_id)

    return submit_episiode(episode)
