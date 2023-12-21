from __future__ import annotations

from typing import Any, NamedTuple

from asyncpraw.reddit import Submission


class Taggable(NamedTuple):
    tagee: Any
    tags: list[str]

    def __bool__(self):
        return bool(self.tags)


class FlairTags(Taggable):
    tagee: Submission
