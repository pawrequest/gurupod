from sqlmodel import Session, select
from gurupod.database import get_session

from asyncpraw.reddit import Subreddit
from asyncpraw.models import WikiPage
from fastapi import APIRouter, Depends

from data.consts import REDDIT_SEND_KEY
from gurupod.writer.writer_funcs_leg.writer_funcs import ep_markup_wiki
from gurupod.models.episode import EpisodeDB
from gurupod.redditbot.reddit import edit_reddit_wiki, submit_episode_subreddit, subreddit_cm, \
    wiki_page_cm

red_router = APIRouter()

@red_router.post('/post_sub')
async def post_episode_subreddit(key: str, episode: EpisodeDB,
                                 subreddit: Subreddit = Depends(subreddit_cm)):
    if key != REDDIT_SEND_KEY:
        return 'wrong key'
    subreddit = await subreddit
    return await submit_episode_subreddit(episode, subreddit)


@red_router.post('/update_wiki')
async def update_wiki_dflt(key, session: Session = Depends(get_session), wiki_page: WikiPage = Depends(wiki_page_cm)):
    if key != REDDIT_SEND_KEY:
        return 'wrong key'
    episodes = session.exec(select(EpisodeDB)).all()
    wiki = await wiki_page
    markup = ep_markup_wiki(episodes)
    res = await edit_reddit_wiki(markup, wiki)
    return res


