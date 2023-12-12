from __future__ import annotations

from typing import List, Sequence

from sqlmodel import Session, select

from gurupod.models.episode import Episode, EpisodeDB, EpisodeOut


def _log_urls(episodes: Sequence[Episode]):
    print("\n".join(['\t' + _.url for _ in episodes[:5]]))
    if len(episodes) > 5:
        print(' ... more ...')
    print('\n')


def _log_existing_urls(episodes: Sequence[Episode]):
    print(f'\nFound {len(episodes)} existing episode links in DB:')
    _log_urls(episodes)


def _log_new_urls(episodes: Sequence[Episode]):
    print(f'\nFound {len(episodes)} new episode links:')
    _log_urls(episodes)


def validate_add(eps: list[Episode], session: Session, commit=False) -> List[Episode | EpisodeOut]:
    valid = [EpisodeDB.model_validate(_) for _ in eps]
    if valid:
        session.add_all(valid)
        if commit:
            session.commit()
            [session.refresh(_) for _ in valid]
        return valid
    else:
        return []


def filter_existing_url(episodes: Sequence[Episode], session: Session) -> tuple[Episode] | None:
    urls_in_db = session.exec(select(EpisodeDB.url)).all()
    if new_eps := tuple(_ for _ in episodes if _.url not in urls_in_db):
        _log_new_urls(new_eps)
    return new_eps or None


