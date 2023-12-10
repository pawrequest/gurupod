from typing import List

from sqlmodel import Session, desc, select

from gurupod.models.episode import Episode, EpisodeDB, EpisodeOut


async def existing_urls_(session: Session) -> list[str]:
    if existing_urls := session.exec(select(EpisodeDB.url).order_by(desc(EpisodeDB.date))).all():
        await log_existing_urls(existing_urls)
        return list(existing_urls)
    return []


async def log_existing_urls(existing_urls):
    print(f'\nFound {len(existing_urls)} existing episode links in DB:')
    print("\n".join(['\t' + _ for _ in existing_urls[:5]]))
    if len(existing_urls) > 5:
        print(' ... more ...')
    print('\n')


def log_new_urls(new_eps):
    print(f'\nFound {len(new_eps)} new episode links:')
    print("\n".join(['\t' + _.url for _ in new_eps[:5]]))
    if len(new_eps) > 5:
        print(' ... more ...')
    print('\n')


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


def filter_existing_names(eps: list[Episode], session: Session) -> List[Episode]:
    names_in_db = session.exec(select(EpisodeDB.name)).all()
    print(f'found {len(names_in_db)} existing episodes in db')
    new_eps = []
    for ep in eps:
        if ep.name in names_in_db:
            print(f'episode {ep.name} already exists in db')
        else:
            print(f'adding episode {ep.name}')
            new_eps.append(ep)
    return new_eps


def filter_existing_url(eps: list[Episode], session: Session) -> List[Episode]:
    urls_in_db = session.exec(select(EpisodeDB.url)).all()
    new_eps = [_ for _ in eps if _.url not in urls_in_db]
    log_new_urls(new_eps)
    return new_eps
