from __future__ import annotations

import pytest
from asyncpraw import Reddit
from asyncpraw.models import WikiPage
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session
from starlette.testclient import TestClient

from data.consts import TEST_WIKI
from gurupod.database import get_session
from gurupod.models.episode import Episode, EpisodeDB
from gurupod.redditguru.reddit import reddit_cm
from main import app

TEST_DB = "sqlite://"
engine = create_engine(
    TEST_DB,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="module")
def episode_interview_fxt():
    return {
        'url': 'https://decoding-the-gurus.captivate.fm/episode/interview-with-daniel-lakens-and-smriti-mehta-on-the-state-of-psychology',
        'name': 'Interview with Daniël Lakens and Smriti Mehta on the state of Psychology',
        'notes': [
            "We are back with more geeky academic discussion than you can shake a stick at. This week we are doing our bit to save civilization by discussing issues in contemporary science, the replication crisis, and open science reforms with fellow psychologists/meta-scientists/podcasters, Daniël Lakens and Smriti Mehta. Both Daniël and Smriti are well known for their advocacy for methodological reform and have been hosting a (relatively) new podcast, Nullius in Verba, all about 'science—what it is and what it could be'. ",
            'We discuss a range of topics including questionable research practices, the implications of the replication crisis, responsible heterodoxy, and the role of different communication modes in shaping discourses. ',
            "Also featuring: exciting AI chat, Lex and Elon being teenage edge lords, feedback on the Huberman episode, and as always updates on Matt's succulents.",
            'Back soon with a Decoding episode!'], 'links': {
            'Nullius in Verba Podcast': 'https://nulliusinverba.podbean.com/',
            "Lee Jussim's Timeline on the Klaus Fiedler Controversy": 'https://unsafescience.substack.com/p/notes-from-a-witch-hunt',
            'a list of articles/sources covering the topic': 'https://unsafescience.substack.com/p/pops-fiasco-orientation-page',
            'Elon Musk: War, AI, Aliens, Politics, Physics, Video Games, and Humanity | Lex Fridman Podcast #400': 'https://www.youtube.com/watch?v=JN3KPFbWCy8',
            "Daniel's MOOC on Improving Your Statistical Inference": 'https://www.coursera.org/learn/statistical-inferences?utm_source=gg&utm_medium=sem&utm_campaign=B2C_APAC__branded_FTCOF_courseraplus_arte_PMax_set3&utm_content=Degree&campaignid=20520161513&adgroupid=&device=c&keyword=&matchtype=&network=x&devicemodel=&adpostion=&creativeid=&hide_mobile_promo&gclid=CjwKCAiAu9yqBhBmEiwAHTx5p5fBUeqyPyuUdxMHD5O0RbTWsScGjvzrsdeuIS3FfEHVuYVnX5PxphoC6DMQAvD_BwE',
            'Critical commentary on Fiedler controversy at Replicability-Index': 'https://replicationindex.com/2022/12/30/klaus-fiedler-is-a-victim-of-his-own-arrogance/'
        }, 'date': '2023-11-18T00:00:00', 'id': 1
    }


@pytest.fixture(scope="function")
def episode_validated_fxt(episode_interview_fxt):
    return Episode.model_validate(episode_interview_fxt)


async def override_subreddit():
    try:
        reddit = Reddit()
        subreddit = await reddit.subreddit('test')
        yield subreddit
    finally:
        reddit.close()

def override_session():
    try:
        session = Session(engine)
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def episode_ipsum_data():
    return [{
        "url": "http://example.com/episode1",
        "name": "Episode 1",
        "notes": ["Note 1"],
        "links": {"link1": "http://example.com/link1"},
        'date': '2023-12-10T02:49:01.240000',
    }]


client = TestClient(app)

app.dependency_overrides[get_session] = override_session
app.dependency_overrides[reddit_cm()] = override_subreddit()


@pytest.fixture()
def test_db():
    Episode.metadata.create_all(bind=engine)
    EpisodeDB.metadata.create_all(bind=engine)
    yield
    Episode.metadata.drop_all(bind=engine)
    EpisodeDB.metadata.drop_all(bind=engine)


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

