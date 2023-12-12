import pytest

from gurupod.writer.writer_funcs_leg.writer_funcs import ep_markup_wiki
from gurupod.writer import RWikiWriter



@pytest.mark.asyncio
async def test_wiki_markup_returns_correct_markup(random_episode_validated, markup_sample):
    markup = ep_markup_wiki(episodes=[random_episode_validated])
    assert isinstance(markup, str)
    assert all([_ in markup for _ in [random_episode_validated.name, random_episode_validated.date.strftime("%A %B %d %Y"),
                                      *[_a for _a in random_episode_validated.notes], *random_episode_validated.links.keys()]])


@pytest.mark.asyncio
async def test_wiki_writer_writes_to_file(random_episode_validated, markup_sample, tmp_path):
    writer = RWikiWriter([random_episode_validated])
    text = RWikiWriter([random_episode_validated]).write_many()
    with open('wiki.md', 'w', encoding='utf8') as outfile:
        outfile.write(text)

