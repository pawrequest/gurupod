import json

from data.consts import EPISODES_JSON, EPISODES_MOD

with open(EPISODES_JSON) as injs:
    eps = json.load(injs)
    out_ = [
        dict(
            name=name,
            url=deets['show_url'],
            notes=deets['show_notes'],
            links=deets['show_links'],
            date=deets['show_date'],
        )
        for name, deets in eps.episodes()
    ]

with open(EPISODES_MOD, 'w') as outjs:
    json.dump(out_, outjs, indent=4)
