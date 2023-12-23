from datetime import datetime

import pytest

from gurupod.models.episode import EpisodeBase
from gurupod.models.responses import EpisodeResponse, EpisodeResponseNoDB, EpisodeWith
from tests.conftest import client


@pytest.mark.asyncio
def test_import_new_episodes(random_episode_json, test_db):
    response = client.post("/eps/put", json=[random_episode_json])
    assert response.status_code == 200
    response_data: EpisodeResponse = response.json()
    ep_response = EpisodeResponse.model_validate(response_data)
    assert isinstance(ep_response, EpisodeResponse)

    episode = EpisodeWith.model_validate(response_data["episodes"][0])
    assert isinstance(episode, EpisodeWith)
    assert episode.notes == random_episode_json["notes"]
    assert episode.links == random_episode_json["links"]
    assert episode.title == random_episode_json["name"]
    assert episode.url == random_episode_json["url"]
    assert episode.date == datetime.fromisoformat(random_episode_json["date"])


@pytest.mark.asyncio
def test_import_existing_episodes(random_episode_json, test_db):
    client.post("/eps/put", json=[random_episode_json])
    response = client.post("/eps/put", json=[random_episode_json])
    assert response.status_code == 200
    assert EpisodeResponse.model_validate(response.json()) == EpisodeResponse.empty()


@pytest.mark.asyncio
async def test_scrape_new_episode(test_db, cached_scrape):
    res = await cached_scrape
    assert isinstance(res.episodes[0], EpisodeBase)


@pytest.mark.skip(reason="duplicates scrape and put")
@pytest.mark.asyncio
def test_fetch_new_episode(test_db):
    response = client.get("/eps/fetch?max_rtn=1")
    assert response.status_code == 200
    data = EpisodeResponse.model_validate(response.json())
    assert isinstance(data.episodes[0], EpisodeWith)
    assert data.meta.length == 1


@pytest.mark.asyncio
def test_read_one_episode(random_episode_json, test_db):
    client.post("/eps/put", json=[random_episode_json])

    response = client.get("/eps/1")
    assert response.status_code == 200
    res = EpisodeResponse.model_validate(response.json())
    assert isinstance(res.episodes[0], EpisodeWith)


@pytest.mark.asyncio
def test_read_one_episode_not_found(test_db):
    response = client.get("/eps/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_read_all_episodes(all_episodes_json, blank_test_db):
    client.post("/eps/put", json=all_episodes_json)
    # await asyncio.sleep(1)
    response = client.get("/eps/")
    assert response.status_code == 200
    res = EpisodeResponse.model_validate(response.json())
    assert res.meta.length == len(all_episodes_json)
    assert isinstance(res.episodes[0], EpisodeWith)


@pytest.mark.asyncio
def test_scrape_empty(test_db):
    response = client.get("/eps/scrape?max_rtn=0")
    assert response.status_code == 200
    assert EpisodeResponse.model_validate(response.json()) == EpisodeResponse.empty()


@pytest.mark.asyncio
def test_maybe_expand(random_episode_validated, test_db):
    ep = EpisodeBase(url=random_episode_validated.url)
    response = client.post("/eps/put", json=[ep.model_dump()])
    assert response.status_code == 200


@pytest.mark.asyncio
def test_scraper_skips_existing(blank_test_db):
    client.get("/eps/scrape?max_rtn=2").json()
    client.get("/eps/fetch?max_rtn=1").json()

    rescraped = client.get("/eps/scrape?max_rtn=1").json()
    rescraped_response = EpisodeResponseNoDB.model_validate(rescraped)
    assert rescraped_response == EpisodeResponseNoDB.empty()
