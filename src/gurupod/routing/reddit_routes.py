from asyncpraw.models import WikiPage
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import REDDIT_SEND_KEY
from gurupod.database import get_session
from gurupod.models.episode import Episode
from gurupod.redditbot.managers import subreddit_cm, wiki_page_cm
from gurupod.redditbot.wrrite_to_web import edit_reddit_wiki, submit_episode_subreddit
from gurupod.writer import RWikiWriter

red_router = APIRouter()


# async def post_episode_subreddit(key: str, episode: EpisodeDB, subreddit: Subreddit = Depends(subreddit_cm)):
@red_router.post("/post_sub")
async def post_episode_subreddit(key: str, sub_name: str, episode: Episode):
    with subreddit_cm(sub_name) as subreddit:
        if key != REDDIT_SEND_KEY:
            return "wrong key"
        subreddit = await subreddit
        return await submit_episode_subreddit(episode, subreddit)


@red_router.post("/update_wiki")
async def update_wiki_dflt(
    key,
    session: Session = Depends(get_session),
    wiki_page: WikiPage = Depends(wiki_page_cm),
):
    if key != REDDIT_SEND_KEY:
        return "wrong key"
    episodes = session.exec(select(Episode)).all()
    wiki = await wiki_page
    writer = RWikiWriter(wiki)
    markup = writer.write_many(episodes)
    res = await edit_reddit_wiki(markup, wiki)
    return res
