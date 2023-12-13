from __future__ import annotations

from typing import List, Sequence

from sqlmodel import Session, select

from gurupod.models.episode import Episode, EpisodeDB


def _log_urls(urls: Sequence[str], msg: str = None):
    print(msg or '')
    print("\n".join(['\t' + _ for _ in urls[:5]]))
    if len(urls) > 5:
        print(' ... more ...')
    print('\n')


def log_existing_urls(urls: Sequence[str]):
    _log_urls(urls, msg=f'\nFound {len(urls)} existing episode links in DB:')


def log_new_urls(urls: Sequence[str]):
    _log_urls(urls, msg=f'\nFound {len(urls)} new episode links:')


def validate_add(eps: Sequence[Episode], session: Session, commit=False) -> tuple[EpisodeDB]:
    valid = [EpisodeDB.model_validate(_) for _ in eps]
    session.add_all(valid)
    if commit:
        session.commit()
        [session.refresh(_) for _ in valid]
    return tuple(valid)


def remove_existing_episodes(episodes: Sequence[Episode], session: Session) -> tuple[Episode]:
    new_urls = remove_existing_urls([_.url for _ in episodes], session)
    new_eps = tuple(_ for _ in episodes if _.url in new_urls)
    return new_eps


def remove_existing_urls(urls: Sequence[str], session: Session) -> tuple[str]:
    urls_in_db = session.exec(select(EpisodeDB.url)).all()
    new_urls = tuple(_ for _ in urls if _ not in urls_in_db)
    log_new_urls(new_urls)
    return new_urls
