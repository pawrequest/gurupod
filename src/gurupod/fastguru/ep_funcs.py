import copy

from sqlmodel import select

from gurupod.models.episode_new import Episode


def add_validate_ep(episode, session) -> Episode:
    try:
        vali = Episode.model_validate(episode)
        session.add(vali)
        session.flush()
        session.refresh(vali)
        return vali
    except Exception as e:
        raise Exception(f'FAILED TO ADD EPISODE {episode.name}\nERROR:{e}')


async def filter_existing(epsdict, session):
    # exist = session.query(Episode).all()
    # exist_names = {e.name for e in exist}
    # exist_names = {name[0] for name in session.query(Episode.name).all()}
    exist_names = session.exec(select(Episode.name)).all()
    new = {name:ep for name, ep in epsdict.items() if name not in exist_names}
    return new


async def commit_new(session):
    try:
        new_made = copy.deepcopy(session.new)
        session.commit()
        rs = [e for e in new_made]
        return rs
    except Exception as e:
        session.rollback()
        raise Exception(f'FAILED TO ADD EPISODES\nERROR:{e}')
