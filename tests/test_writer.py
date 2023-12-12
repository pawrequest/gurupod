import pytest

from gurupod.writer.writer_funcs_leg.writer_funcs import ep_markup_wiki
from gurupod.writer import RWikiWriter



@pytest.mark.asyncio
async def test_wiki_markup_returns_correct_markup(episode_validated_fxt, markup_sample):
    markup = ep_markup_wiki(episodes=[episode_validated_fxt])
    assert isinstance(markup, str)
    assert all([_ in markup for _ in [episode_validated_fxt.name, episode_validated_fxt.date.strftime("%A %B %d %Y"),
                                      *[_a for _a in episode_validated_fxt.notes], *episode_validated_fxt.links.keys()]])


@pytest.mark.asyncio
async def test_wiki_writer_writes_to_file(episode_validated_fxt, markup_sample, tmp_path):
    writer = RWikiWriter([episode_validated_fxt])
    text = RWikiWriter([episode_validated_fxt]).write_many()
    with open('wiki.md', 'w', encoding='utf8') as outfile:
        outfile.write(text)

