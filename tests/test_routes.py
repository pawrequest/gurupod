import asyncio
from datetime import datetime

import pytest

from gurupod.models.episode import Episode, EpisodeOut, EpisodeResponse, EpisodeResponseNoDB
from tests.conftest import client


@pytest.mark.asyncio
def test_import_new_episodes(random_episode_json, test_db):
    response = client.post("/eps/put_ep", json=[random_episode_json])
    assert response.status_code == 200
    response_data: EpisodeResponse = response.json()
    ep_response = EpisodeResponse.model_validate(response_data)
    assert isinstance(ep_response, EpisodeResponse)

    episode = EpisodeOut.model_validate(response_data['episodes'][0])
    assert isinstance(episode, EpisodeOut)
    assert episode.notes == random_episode_json['notes']
    assert episode.links == random_episode_json['links']
    assert episode.name == random_episode_json['name']
    assert episode.url == random_episode_json['url']
    assert episode.date == datetime.fromisoformat(random_episode_json['date'])


@pytest.mark.asyncio
def test_import_existing_episodes(random_episode_json, test_db):
    client.post("/eps/put_ep", json=[random_episode_json])
    response = client.post("/eps/put_ep", json=[random_episode_json])
    assert response.status_code == 200
    assert EpisodeResponse.model_validate(response.json()) == EpisodeResponse.no_new()


@pytest.mark.asyncio
def test_scrape_new_episode(test_db):
    response = client.get("/eps/scrape1")
    assert response.status_code == 200
    res = EpisodeResponseNoDB.model_validate(response.json())
    assert isinstance(res.episodes[0], Episode)



@pytest.mark.asyncio
def test_fetch_new_episode(test_db):
    response = client.get("/eps/fetch1")
    assert response.status_code == 200
    data = EpisodeResponse.model_validate(response.json())
    assert isinstance(data.episodes[0], EpisodeOut)
    assert data.meta.length == 1




@pytest.mark.asyncio
def test_read_one_episode(random_episode_json, test_db):
    client.post("/eps/put_ep", json=[random_episode_json])

    response = client.get("/eps/1")
    assert response.status_code == 200
    res = EpisodeResponse.model_validate(response.json())
    assert isinstance(res.episodes[0], EpisodeOut)


@pytest.mark.asyncio
def test_read_one_episode_not_found(test_db):
    response = client.get("/eps/9999")
    assert response.status_code == 404




@pytest.mark.asyncio
async def test_read_all_episodes(all_episodes_json, blank_test_db):
    client.post("/eps/put_ep", json=all_episodes_json)
    await asyncio.sleep(1)
    response = client.get("/eps/")
    assert response.status_code == 200
    res = EpisodeResponse.model_validate(response.json())
    assert res.meta.length == len(all_episodes_json)
    assert isinstance(res.episodes[0], EpisodeOut)



@pytest.mark.asyncio
def test_fetch_empty(test_db):
    response = client.get("/eps/fetch0")
    assert response.status_code == 200
    assert EpisodeResponse.model_validate(response.json()) == EpisodeResponse.no_new()


@pytest.mark.asyncio
def test_maybe_expand(random_episode_validated, test_db):
    ep = Episode(
        url=random_episode_validated.url)
    response = client.post("/eps/put_ep", json=[ep.model_dump()])
    assert response.status_code == 200


@pytest.mark.asyncio
def test_scraper_skips_existing(blank_test_db):
    two_scraped = client.get("/eps/scrape2").json()
    response_1 = EpisodeResponseNoDB.model_validate(two_scraped)
    scraped_ep1, scraped_ep2 = response_1.episodes

    fetched = client.get("/eps/fetch1").json()
    fetched_response = EpisodeResponse.model_validate(fetched)
    fetched_ep = fetched_response.episodes[0]

    rescraped = client.get("/eps/scrape1").json()
    rescraped_response = EpisodeResponseNoDB.model_validate(rescraped)
    rescraped_ep1 = rescraped_response.episodes[0]

    assert rescraped_ep1 != scraped_ep1
    assert scraped_ep2 == rescraped_ep1
