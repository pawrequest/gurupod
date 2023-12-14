from __future__ import annotations

from asyncpraw.reddit import Submission, Subreddit


async def submission_in_stream_by_id(submission_id: str, subreddit: Subreddit) -> Submission:
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if submission_id == submission.id:
            return submission



async def title_in_subreddit(title, subreddit: Subreddit) -> Submission:
    async for submission in subreddit.stream.submissions():
        submission: Submission = submission
        if title in submission.title:
            return submission

