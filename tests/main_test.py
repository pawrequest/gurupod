import datetime

import pytest
from bs4 import BeautifulSoup

from data.consts import MAIN_URL
from src.gurupod.episode import _url_from_pagenum, ep_soup_from_link, ep_soup_date, ep_soup_notes, \
    ep_soup_links


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


def test_ep_soup_from_link(ep_url):
    soup = ep_soup_from_link(ep_url)
    assert isinstance(soup, BeautifulSoup)

