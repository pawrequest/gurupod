import pytest

from src.gurupod.markupguru.markup_writer import episodes_wiki

@pytest.mark.asyncio
async def test_wiki_markup_returns_correct_markup(episode_validated_fxt, markup_sample):
    markup = episodes_wiki(episodes=[episode_validated_fxt])
    assert isinstance(markup, str)
    assert markup == markup_sample



