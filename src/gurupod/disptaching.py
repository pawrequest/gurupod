from __future__ import annotations

import asyncio
from asyncio import Queue, create_task

from aiohttp import ClientSession


#
# class Dispatcher:
#     def __init__(self, jobs, aio_session: ClientSession, job_func, job_getter, queue_timeout=None, **kwargs):
#         self.queue = Queue()
#         self.aio_session = aio_session
#         self.queue_timeout = queue_timeout
#         self.jobs:dict[Awaitable, dict[str,str]] = jobs
#         self.job_getter:AsyncGenerator = job_getter
#         self.kwargs = kwargs
#
#
#     async def __call__(self):
#         async for _ in self.job_getter:
#             for job, params in self.jobs.items():
#                 task = create_task(job(**params, aio_session=self.aio_session))
#                 await self.queue.put(task)
#             ...
#         await asyncio.wait_for(self.queue.join(), timeout=self.queue_timeout)

# class Dispatcher:
#     def __init__(self, task_dict: dict[], aio_session: ClientSession, job_getter: AsyncGenerator,
#                  queue_timeout=None):
from typing import Callable, Any, Coroutine

from bs4 import BeautifulSoup

from data.consts import MAIN_URL
from gurupod.scrape import _get_response, listing_pages_


class JobGetter:
    def __init__(self, job_sources, job_retriever: Callable):
        self.job_sources = job_sources
        self.job_retriever = job_retriever

    def __aiter__(self):
        for job_source in self.job_sources:
            yield from self.job_retriever(job_source)


def get_job_getter(aio_session: ClientSession, url = MAIN_URL):
    jg = JobGetter(
        job_sources=listing_pages_(url, aio_session),
        job_retriever=_get_episdode_urls_new
    )
    return jg
class Dispatcher:
    def __init__(self,
                 task_funcs: list[Callable[[Any], Coroutine[Any, Any, Any]]],
                 job_getter: JobGetter, queue_timeout: int or None = None,
                 aio_session: ClientSession or None = None):
        self.queue = Queue()
        self.aio_session = aio_session or ClientSession()
        self.queue_timeout = queue_timeout
        self.task_funcs = task_funcs
        self.job_getter = job_getter

    async def __call__(self):
        return await self.do_jobs()

    async def _dispatch(self):
        async for job in self.job_getter:
            for sub_task in self.task_funcs:
                task = create_task(sub_task(job))
                await self.queue.put(task)

        await asyncio.wait_for(self.queue.join(), timeout=self.queue_timeout)

    async def _worker(self):
        while True:
            task = await self.queue.get()
            try:
                await task
            except Exception as e:
                print(f"Task raised an exception: {e}")
            finally:
                self.queue.task_done()

    async def do_jobs(self, dispatch_timeout: int or None = 30):
        workers = [create_task(self._worker()) for _ in range(5)]
        dispatcher = create_task(self._dispatch())

        try:
            await asyncio.wait([dispatcher], timeout=dispatch_timeout)
        except asyncio.TimeoutError:
            print("Timeout")
        finally:
            for worker in workers:
                worker.cancel()
            dispatcher.cancel()
            await asyncio.gather(*workers, dispatcher, return_exceptions=True)



async def _get_episdode_urls_new(listing_page: str, aio_session: ClientSession):
    text = await _get_response(listing_page, aio_session)
    listing_soup = BeautifulSoup(text, "html.parser")
    episodes_res = listing_soup.select(".episode")
    # return [str(ep_soup.select_one(".episode-title a")['href']) for ep_soup in episodes_res]
    for ep_soup in episodes_res:
        yield str(ep_soup.select_one(".episode-title a")['href'])



async def main():
    async with ClientSession() as aio_session:
        task_funcs = [_get_episdode_urls_new]

        disp = Dispatcher(task_funcs=task_funcs, )
