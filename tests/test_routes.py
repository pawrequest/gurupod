from datetime import datetime

import pytest

from gurupod.models.episode import Episode, EpisodeOut, EpisodeResponse
from tests.conftest import client


@pytest.mark.asyncio
def test_import_new_episodes(episode_ipsum_data, test_db):
    response = client.post("/eps/put_ep", json=episode_ipsum_data)
    assert response.status_code == 200
    response_data: EpisodeResponse = response.json()
    ep_response = EpisodeResponse.model_validate(response_data)
    assert isinstance(ep_response, EpisodeResponse)

    episode = EpisodeOut.model_validate(response_data['episodes'][0])
    assert isinstance(episode, EpisodeOut)
    assert episode.notes == episode_ipsum_data[0]['notes']
    assert episode.links == episode_ipsum_data[0]['links']
    assert episode.name == episode_ipsum_data[0]['name']
    assert episode.url == episode_ipsum_data[0]['url']
    assert episode.date == datetime.fromisoformat(episode_ipsum_data[0]['date'])


@pytest.mark.asyncio
def test_import_existing_episodes(episode_ipsum_data, test_db):
    client.post("/eps/put_ep", json=episode_ipsum_data)
    response = client.post("/eps/put_ep", json=episode_ipsum_data)
    assert response.status_code == 200
    assert EpisodeResponse.model_validate(response.json()) == EpisodeResponse.no_new()


@pytest.mark.asyncio
def test_scrape_new_episode(test_db):
    response = client.get("/eps/scrape1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
def test_fetch_new_episode(test_db):
    response = client.get("/eps/fetch1")
    assert response.status_code == 200
    assert isinstance(response.json()[0]['name'], str)
    assert isinstance(response.json()[0]['url'], str)
    assert isinstance(response.json()[0]['notes'], list)
    assert isinstance(response.json()[0]['links'], dict)
    assert isinstance(response.json()[0]['date'], str)


@pytest.mark.asyncio
def test_read_one_episode(episode_ipsum_data, test_db):
    client.post("/eps/put_ep", json=episode_ipsum_data)

    response = client.get("/eps/1")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    res = response.json()
    res.pop('id')
    assert res == episode_ipsum_data[0]


@pytest.mark.asyncio
def test_read_one_episode_not_found(test_db):
    response = client.get("/eps/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
def test_read_all_episodes(episode_ipsum_data, test_db):
    client.post("/eps/put_ep", json=episode_ipsum_data)

    response = client.get("/eps/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    res = EpisodeOut.model_validate(response.json()[0])
    assert isinstance(res, EpisodeOut)


@pytest.mark.asyncio
def test_fetch_empty(test_db):
    response = client.get("/eps/fetch0")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
def test_maybe_expand(episode_interview_fxt, test_db):
    ep = Episode(
        url="https://decoding-the-gurus.captivate.fm/episode/interview-with-daniel-lakens-and-smriti-mehta-on-the-state-of-psychology")
    response = client.post("/eps/put_ep", json=[ep.dict()])
    assert response.status_code == 200
    assert response.json() == [episode_interview_fxt]


@pytest.mark.asyncio
def test_scraper_skips_existing(test_db):
    two_scraped = client.get("/eps/scrape2")
    scraped_ep1, scraped_ep2 = two_scraped.json()
    val1 = Episode.model_validate(scraped_ep1)
    client.get("/eps/fetch1")
    rescraped = client.get("/eps/scrape1").json()[0]
    val2 = Episode.model_validate(rescraped)

    assert isinstance(val1, Episode)
    assert isinstance(val2, Episode)
    assert rescraped == scraped_ep2
