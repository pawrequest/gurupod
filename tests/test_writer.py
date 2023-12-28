import pytest

from gurupod.podcast_monitor.writer import RWikiWriter


@pytest.mark.asyncio
async def test_wiki_writer(random_episode_validated, markup_sample):
    writer = RWikiWriter([random_episode_validated])
    markup = writer.write_many()
    assert isinstance(markup, str)
    assert all(
        [
            _ in markup
            for _ in [
                random_episode_validated.title,
                random_episode_validated.date.strftime("%A %B %d %Y"),
                *[_a for _a in random_episode_validated.notes],
                *random_episode_validated.links.keys(),
            ]
        ]
    )
