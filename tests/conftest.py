from __future__ import annotations

import json
from random import randint

import pytest
from asyncpraw import Reddit
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session
from starlette.testclient import TestClient

from gurupod.database import get_session
from gurupod.models.episode import Episode, EpisodeDB
from gurupod.redditbot.managers import reddit_cm
from main import app

TEST_DB = "sqlite://"
ENGINE = create_engine(
    TEST_DB,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


async def override_subreddit():
    try:
        reddit = Reddit()
        subreddit = await reddit.subreddit('test')
        yield subreddit
    finally:
        await reddit.close()


def override_session():
    try:
        session = Session(ENGINE)
        yield session
    finally:
        session.close()


client = TestClient(app)

app.dependency_overrides[get_session] = override_session
app.dependency_overrides[reddit_cm()] = override_subreddit()


@pytest.fixture(scope="session")
def all_episodes_json():
    with open('episodes.json', 'r') as f:
        return json.load(f)


@pytest.fixture(scope="function")
def random_episode_json(all_episodes_json):
    yield all_episodes_json[randint(0, len(all_episodes_json)-1)]


@pytest.fixture(scope="function")
def random_episode_validated(random_episode_json):
    return Episode.model_validate(random_episode_json)


@pytest.fixture(scope="function")
def episode_josh():
    name = 'Interview with Josh Szeps, The Rumble from Downunder'
    with open('episodes.json', 'r') as f:
        eps = json.load(f)
        for ep in eps:
            if ep['name'] == name:
                return Episode.model_validate(ep)



@pytest.fixture(scope="function")
def episodes_weird(all_episodes_json):
    names = ['Interview with Josh Szeps, The Rumble from Downunder',
             'Interview with the Conspirituality Trio: Navigating the Chakras of Conspiracy',]
    weird = [_ for _ in all_episodes_json if _['name'] in names]
    return [Episode.model_validate(_) for _ in weird]






@pytest.fixture(scope="session")
def test_db():
    Episode.metadata.create_all(bind=ENGINE)
    EpisodeDB.metadata.create_all(bind=ENGINE)
    yield
    Episode.metadata.drop_all(bind=ENGINE)
    EpisodeDB.metadata.drop_all(bind=ENGINE)

@pytest.fixture(scope="function")
def blank_test_db(test_db):
    Episode.metadata.drop_all(bind=ENGINE)
    EpisodeDB.metadata.drop_all(bind=ENGINE)
    Episode.metadata.create_all(bind=ENGINE)
    EpisodeDB.metadata.create_all(bind=ENGINE)
    yield



@pytest.fixture(scope="module")
def markup_sample():
    return """# Interview with Daniël Lakens and Smriti Mehta on the state of Psychology
 
[play on captivate.fm](https://decoding-the-gurus.captivate.fm/episode/interview-with-daniel-lakens-and-smriti-mehta-on-the-state-of-psychology)
### Published Saturday November 18 2023
 
### Show Notes

We are back with more geeky academic discussion than you can shake a stick at. This week we are doing our bit to save civilization by discussing issues in contemporary science, the replication crisis, and open science reforms with fellow psychologists/meta-scientists/podcasters, Daniël Lakens and Smriti Mehta. Both Daniël and Smriti are well known for their advocacy for methodological reform and have been hosting a (relatively) new podcast, Nullius in Verba, all about 'science—what it is and what it could be'. 

We discuss a range of topics including questionable research practices, the implications of the replication crisis, responsible heterodoxy, and the role of different communication modes in shaping discourses. 

Also featuring: exciting AI chat, Lex and Elon being teenage edge lords, feedback on the Huberman episode, and as always updates on Matt's succulents.

Back soon with a Decoding episode!

### Show Links

[Nullius in Verba Podcast](https://nulliusinverba.podbean.com/)

[Lee Jussim's Timeline on the Klaus Fiedler Controversy](https://unsafescience.substack.com/p/notes-from-a-witch-hunt)

[a list of articles/sources covering the topic](https://unsafescience.substack.com/p/pops-fiasco-orientation-page)

[Elon Musk: War, AI, Aliens, Politics, Physics, Video Games, and Humanity | Lex Fridman Podcast #400](https://www.youtube.com/watch?v=JN3KPFbWCy8)

[Daniel's MOOC on Improving Your Statistical Inference](https://www.coursera.org/learn/statistical-inferences?utm_source=gg&utm_medium=sem&utm_campaign=B2C_APAC__branded_FTCOF_courseraplus_arte_PMax_set3&utm_content=Degree&campaignid=20520161513&adgroupid=&device=c&keyword=&matchtype=&network=x&devicemodel=&adpostion=&creativeid=&hide_mobile_promo&gclid=CjwKCAiAu9yqBhBmEiwAHTx5p5fBUeqyPyuUdxMHD5O0RbTWsScGjvzrsdeuIS3FfEHVuYVnX5PxphoC6DMQAvD_BwE)

[Critical commentary on Fiedler controversy at Replicability-Index](https://replicationindex.com/2022/12/30/klaus-fiedler-is-a-victim-of-his-own-arrogance/)


 
 ---"""
