from __future__ import annotations

from typing import Union

from gurupod.models.guru import Guru
from gurupod.models.episode import Episode
from gurupod.models.reddit_thread import RedditThread

UI_ELEMENT = Union[Guru, Episode, RedditThread]
