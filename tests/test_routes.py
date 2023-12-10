from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, StaticPool, create_engine

from gurupod.database import get_session
from main import app
from gurupod.models import episode
from gurupod.models.episode import Episode, EpisodeDB, EpisodeOut

TEST_DB = "sqlite://"

engine = create_engine(
    TEST_DB,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_session():
    try:
        session = Session(engine)
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = override_session


####

@pytest.fixture(scope="module")
def episode_data():
    return [{
        "url": "http://example.com/episode1",
        "name": "Episode 1",
        "notes": ["Note 1"],
        "links": {"link1": "http://example.com/link1"},
        'date': '2023-12-10T02:49:01.240000',
    }]


client = TestClient(app)


@pytest.fixture()
def test_db():
    Episode.metadata.create_all(bind=engine)
    EpisodeDB.metadata.create_all(bind=engine)
    yield
    Episode.metadata.drop_all(bind=engine)
    EpisodeDB.metadata.drop_all(bind=engine)


def test_import_new_episodes(episode_data, test_db):
    response = client.post("/eps/import", json=episode_data)
    assert response.status_code == 200
    response_data: [episode.EpisodeOut] = response.json()
    resp = EpisodeOut.model_validate(response_data[0])
    assert isinstance(resp, EpisodeOut)
    assert resp.notes == episode_data[0]['notes']
    assert resp.links == episode_data[0]['links']
    assert resp.name == episode_data[0]['name']
    assert resp.url == episode_data[0]['url']
    assert resp.date == datetime.fromisoformat(episode_data[0]['date'])


def test_import_existing_episodes(episode_data, test_db):
    client.post("/eps/import", json=episode_data)
    response = client.post("/eps/import", json=episode_data)
    assert response.status_code == 200
    assert response.json() == []


def test_scrape_new_episode(test_db):
    response = client.get("/eps/scrape1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_fetch_new_episode(test_db):
    response = client.get("/eps/fetch1")
    assert response.status_code == 200
    assert isinstance(response.json()[0]['name'], str)
    assert isinstance(response.json()[0]['url'], str)
    assert isinstance(response.json()[0]['notes'], list)
    assert isinstance(response.json()[0]['links'], dict)
    assert isinstance(response.json()[0]['date'], str)


def test_read_one_episode(episode_data, test_db):
    client.post("/eps/import", json=episode_data)

    response = client.get("/eps/1")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    res = response.json()
    res.pop('id')
    assert res == episode_data[0]


def test_read_one_episode_not_found(test_db):
    response = client.get("/eps/9999")
    assert response.status_code == 404


def test_read_all_episodes(episode_data, test_db):
    client.post("/eps/import", json=episode_data)

    response = client.get("/eps/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    res = EpisodeOut.model_validate(response.json()[0])
    assert isinstance(res, EpisodeOut)
