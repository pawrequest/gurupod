import asyncio
import datetime

import aiohttp
import pytest
from bs4 import BeautifulSoup

from gurupod.data.consts import MAIN_URL
from gurupod.episodes import _url_from_pagenum, ep_soup_date, ep_soup_from_link, ep_soup_links, \
    ep_soup_notes

@pytest.fixture
async def session_():
    session = aiohttp.ClientSession()
    yield session
    await session.close()

# @pytest.fixture
# async def session_():
#     async with aiohttp.ClientSession() as session:
#         yield session

@pytest.fixture
def ep_soup_():
    html = '<div class="publish-date">2022-01-01</div><div class="show-notes"><p>Note 1</p><p>Note 2</p><a href="http://link1.com">Link 1</a><a href="http://link2.com">Link 2</a></div>'
    yield BeautifulSoup(html, 'html.parser')


def test_ep_soup_date(ep_soup_):
    date_ = ep_soup_date(ep_soup_)
    assert isinstance(date_, datetime.date)


def test_ep_soup_notes(ep_soup_):
    notes = ep_soup_notes(ep_soup_)
    assert isinstance(notes, list)
    assert all(isinstance(note, str) for note in notes)


def test_ep_soup_links(ep_soup_):
    links = ep_soup_links(ep_soup_)
    assert isinstance(links, dict)
    assert all(isinstance(key, str) and isinstance(value, str) for key, value in links.items())


@pytest.fixture
def ep_url():
    yield _url_from_pagenum(MAIN_URL, 0)

#
# def test_ep_soup_from_link(ep_url, session_):
#     soup = ep_soup_from_link(ep_url, session_)
#     assert isinstance(soup, BeautifulSoup)
#

@pytest.mark.xfail
@pytest.mark.asyncio
async def test_ep_soup_from_link(ep_url, session_):
    soup = asyncio.run(ep_soup_from_link(ep_url, session_))
    assert isinstance(soup, BeautifulSoup)