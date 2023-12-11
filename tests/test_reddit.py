import asyncio
from asyncio import create_task, wait

import pytest
from asyncpraw.models import WikiPage
from asyncpraw.reddit import Reddit, Submission, Subreddit

from data.consts import GURU_SUB, TEST_SUB, TEST_WIKI
from data.gurunames import GURUS
from gurupod.redditguru.reddit import SubmissionFlairs, apply_flair_one, edit_reddit_wiki, \
    stream_submissioin_flairs, submission_id_in_subreddit, \
    one_submission_flairs, apply_flair, reddit_cm, \
    stream_submissions_to_tag, submit_episode_subreddit, \
    subreddit_cm, wiki_page_cm


@pytest.mark.asyncio
async def test_reddit_cm():
    async with reddit_cm() as reddit:
        assert isinstance(reddit, Reddit)


@pytest.mark.asyncio
async def test_subred_cm():
    async with subreddit_cm() as subreddit:
        assert isinstance(subreddit, Subreddit)


@pytest.mark.asyncio
async def test_wiki_cm():
    async with wiki_page_cm() as wiki:
        assert isinstance(wiki, WikiPage)


@pytest.mark.asyncio
async def test_edit_wiki(markup_sample):
    async with wiki_page_cm(GURU_SUB, TEST_WIKI) as wiki:
        await edit_reddit_wiki('', wiki)
        await wiki.load()
        assert wiki.content_md == ''

        await edit_reddit_wiki(markup_sample, wiki)
        await wiki.load()
        assert wiki.content_md == markup_sample

        cl = await edit_reddit_wiki('', wiki)


@pytest.mark.asyncio
async def test_post_to_subreddit(episode_validated_fxt):
    async with subreddit_cm(TEST_SUB) as subreddit:
        posted = await submit_episode_subreddit(episode_validated_fxt, subreddit)
        found = await submission_id_in_subreddit(posted.id, subreddit)
        assert found == posted



async def worker_bee(queue: asyncio.Queue):
    while True:
        task = await queue.get()
        print(f"Processing {task}...")
        try:
            await task
        except Exception as e:
            print(f"Task raised an exception: {e}")
        finally:
            queue.task_done()

async def dispatch_tasks(subreddit: Subreddit, queue: asyncio.Queue):
    async for sub_flairs in stream_submissioin_flairs(subreddit):
        print(f"Dispatching {sub_flairs}...")
        await queue.put(sub_flairs)


@pytest.mark.asyncio
async def test_submissions_to_flair():
    queue = asyncio.Queue()
    workers = [create_task(worker_bee(queue)) for _ in range(5)]

    async with subreddit_cm(GURU_SUB) as subreddit:
        dispatcher = create_task(dispatch_tasks(subreddit, queue))
        print("Waiting for tasks to complete...")

        try:
            await asyncio.wait_for(queue.join(), timeout=30)  # Set timeout as needed
        except asyncio.TimeoutError:
            print("Processing timeout reached")
        finally:
            # Cancel worker and dispatcher tasks
            for worker in workers:
                worker.cancel()
            dispatcher.cancel()
            await asyncio.gather(*workers, dispatcher, return_exceptions=True)

    print("All tasks completed or timeout reached")




# @pytest.mark.asyncio
# async def test_submissions_to_flair():
#
#     do_queue = asyncio.Queue()
#     with subreddit_cm(TEST_SUB) as subreddit:
#         tasks = stream_flair_tasks(subreddit)
#
#
#
#         async for submission, flairs in stream_submissions_to_tag(subreddit, tags=GURUS):
#             gf = SubmissionFlairs(submission, flairs)
#             to_flair.append(create_task(apply_flair_one(gf)))
#
#             assert isinstance(submission, Submission)
#             assert isinstance(flairs, list)
#


    # async def consume_submissions(submissions):
    #     async for gf in submissions:
    #         ...
    #
    # async with subreddit_cm(DTG_SUB) as subreddit:
    #     subsy = stream_submissions_to_flair(subreddit, gurus=GURUS)
    #
    #     tasks = [asyncio.create_task(consume_submissions(sub)) for sub in subsy]
    #     try:
    #         await asyncio.gather(*tasks, )
    #     except asyncio.TimeoutError:
    #         [_.cancel() for _ in tasks]
    #         await asyncio.wait_for(tasks, timeout=10)
    #     finally:
    #         await subsy.aclose()
    #         ...


@pytest.mark.asyncio
async def test_apply_flair_one():
    async with subreddit_cm(GURU_SUB) as subreddit:
        gf = await one_submission_flairs(subreddit, gurus=GURUS)
        res = await apply_flair([gf])
        ...
