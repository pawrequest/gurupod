from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import REDDIT_SEND_KEY, WIKINAME
from gurupod import episodes_markup
from gurupod.database import get_session
from gurupod.markupguru.markup_reddit import reddit_functions
from gurupod.markupguru.wiki_writer import wiki_functions
from gurupod.models.episode import EpisodeDB
from gurupod.redditguru.reddit import edit_reddit_wiki, post_episode

red_router = APIRouter()

@red_router.get('/new_episode_reddit/{key}/{ep_id}')
async def post_episode_subreddit(key, ep_id, session: Session = Depends(get_session)):
    if key != REDDIT_SEND_KEY:
        return 'wrong key'
    episode = session.get(EpisodeDB, ep_id)

    return post_episode(episode, sub_reddit='test')


@red_router.get('/update_wiki/{key}')
async def update_wiki(key, session: Session = Depends(get_session)):
    if key != REDDIT_SEND_KEY:
        return 'wrong key'
    episodes = session.exec(select(EpisodeDB)).all()
    markup = episodes_markup(episodes, wiki_functions)
    return edit_reddit_wiki(markup)
