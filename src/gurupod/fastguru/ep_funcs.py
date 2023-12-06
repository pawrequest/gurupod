import copy

from gurupod.models.episode_new import Episode


def validate_add_ep(episode, session):
    try:
        vali = Episode.model_validate(episode)
        session.add(vali)
        session.refresh(vali)
        return vali
    except Exception as e:
        raise Exception(f'FAILED TO ADD EPISODE {episode.name}\nERROR:{e}')


async def filter_existing(epsdict, session):
    exist = session.query(Episode).all()
    exist_names = {e.name for e in exist}
    new = [e for e in epsdict if e['name'] not in exist_names]
    return new


async def commit_new(session):
    try:
        new_made = copy.deepcopy(session.new)
        session.commit()
        return [e for e in new_made]
    except Exception as e:
        session.rollback()
        raise Exception(f'FAILED TO ADD EPISODES\nERROR:{e}')
