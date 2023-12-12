from __future__ import annotations

import asyncio
from asyncio import create_task
from typing import AsyncGenerator

from aiohttp import ClientSession

from data.consts import MAIN_URL
from gurupod.scrape import _get_episdode_urls, listing_pages_

class Dispatcher:
    def __init__(self, queue: asyncio.Queue, aio_session: ClientSession, job_func, job_getter, queue_timeout=None, **kwargs):
        self.queue = queue
        self.aio_session = aio_session
        self.queue_timeout = queue_timeout
        self.job_func = job_func
        self.job_getter:AsyncGenerator = job_getter
        if kwargs.get('main_url'):
            self.main_url = kwargs.get('main_url')


    async def __call__(self):
        async for _ in self.job_getter(self.main_url, self.aio_session):
            task = create_task(_get_episdode_urls(listing_page=_, aio_session=self.aio_session))
            await self.queue.put(task)
            ...
        await asyncio.wait_for(self.queue.join(), timeout=self.queue_timeout)
async def _worker(queue: asyncio.Queue):
    while True:
        task = await queue.get()
        try:
            await task
        except Exception as e:
            print(f"Task raised an exception: {e}")
        finally:
            queue.task_done()


async def _dispatcher(queue: asyncio.Queue, aio_session: ClientSession, queue_timeout=None):
    for listing_ in await listing_pages_(MAIN_URL, aio_session):
        task = create_task(_get_episdode_urls(listing_page=listing_, aio_session=aio_session))
        await queue.put(task)
        ...
    await asyncio.wait_for(queue.join(), timeout=queue_timeout)


async def do_jobs(aio_session:ClientSession, dispatch_timeout: int or None = 30):
    queue = asyncio.Queue()
    workers = [create_task(_worker(queue)) for _ in range(5)]
    dispatcher = create_task(_dispatcher(queue, aio_session))

    try:
        await asyncio.wait([dispatcher], timeout=dispatch_timeout)
    except asyncio.TimeoutError:
        print("Timeout")
    finally:
        for worker in workers:
            worker.cancel()
        dispatcher.cancel()
        await asyncio.gather(*workers, dispatcher, return_exceptions=True)


async def main():
    async with ClientSession() as aio_session:
        await do_jobs(aio_session, dispatch_timeout=None)


