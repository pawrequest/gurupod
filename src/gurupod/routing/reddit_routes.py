from datetime import datetime

from asyncpraw.models import Submission, WikiPage
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from data.consts import REDDIT_SEND_KEY
from gurupod.database import get_session
from gurupod.gurulog import get_logger
from gurupod.models.episode import Episode
from gurupod.models.reddit_model import RedditThread, RedditThreadBase
from gurupod.models.responses import RedditThreadWith
from gurupod.redditbot.managers import subreddit_cm, wiki_page_cm
from gurupod.redditbot.write_to_web import edit_reddit_wiki, submit_episode_subreddit
from gurupod.routing.episode_routes import assign_gurus
from gurupod.writer import RWikiWriter

logger = get_logger()
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


@red_router.post("/import_thread", response_model=RedditThreadWith)
async def put_thread(
    key: str,
    submission_id: str,
    session: Session = Depends(get_session),
):
    if key != REDDIT_SEND_KEY:
        return "wrong key"

    submission = await Submission.fetch(submission_id)


async def save_submission(session: Session, submission: Submission):
    try:
        logger.info(f"Saving submission: {submission.title}")
        cr_date = datetime.fromtimestamp(submission.created_utc)
        submission_data = RedditThreadBase(
            reddit_id=submission.id,
            title=submission.title,
            shortlink=submission.shortlink,
            created_datetime=cr_date,
        )
        thread_ = RedditThread.model_validate(submission_data)
        assigned = await assign_gurus([thread_], session)
        session.add(thread_)
        session.commit()
        return thread_
    except Exception as e:
        logger.error(f"Error processing submission for DB: {e}")
