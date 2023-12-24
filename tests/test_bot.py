# import asyncio
# from asyncio import Queue
#
# import pytest
#
# from data.consts import TEST_SUB, GURU_SUB
# from gurupod.redditbot.managers import subreddit_cm
# from gurupod.redditbot.monitor import submission_monitor
# from gurupod.redditbot.write_to_web import submit_episode_subreddit
#
#
# @pytest.mark.asyncio
# async def test_monitor_detects_new_posts(random_episode_validated):
#     async with subreddit_cm(TEST_SUB) as subreddit:
#         async for sub in submission_monitor(subreddit_name=GURU_SUB):
#             await save_submission(session, sub)
#             yield
#
#         # Post a new submission
#         posted = await submit_episode_subreddit(random_episode_validated, subreddit)
#
#         # Allow some time for the monitor to detect the new post
#         await asyncio.sleep(2)  # Adjust this based on expected latency
#
#         # Terminate the monitor task
#         monitor_task.cancel()
#         try:
#             await monitor_task
#         except asyncio.CancelledError:
#             pass  # Expected due to task cancellation
#
#         # Retrieve and check if the new post was detected and processed by the monitor
#         # This step depends on how you track or log processed posts in your application
#         # For example, check if the post's flair was updated or if a log entry was created
#
#         # Assertions and additional checks go here
