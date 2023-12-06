import copy

from sqlmodel import Session, select

from gurupod.models.episode_new import Episode, EpisodeCreate


def add_validate_ep(episode, session:Session) -> Episode:
    try:
        vali = Episode.model_validate(episode)
        session.add(vali)
        session.flush()
        session.refresh(vali)
        return vali
    except Exception as e:
        raise Exception(f'FAILED TO ADD EPISODE {episode.name}\nERROR:{e}')


async def filter_existing(eps: list[EpisodeCreate], session):
    exist_names = session.exec(select(Episode.name)).all()
    new = [ep for ep in eps if ep.name not in exist_names]
    return new


async def filter_existing2(eps: [EpisodeCreate], session):
    exist_names = session.exec(select(Episode.name)).all()
    return [ep for ep in eps if ep.name not in exist_names]

    # new = {name:ep for name, ep in epsdict.items() if name not in exist_names}
    # return new


async def commit_new(session: Session):
    try:
        if new_made := copy.deepcopy(session.new):
            session.commit()
            return new_made
    except Exception as e:
        breakpoint()
        session.rollback()
        raise Exception(f'FAILED TO ADD EPISODES\nERROR:{e}')
