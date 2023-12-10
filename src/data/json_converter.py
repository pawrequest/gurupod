import json

from data.consts import EPISODES_JSON, EPISODES_MOD

with open(EPISODES_JSON) as injs:
    eps = json.load(injs)
    out_dict = []
    for name, deets in eps.items():
        new_dict = dict(
            name=name,
            url=deets['show_url'],
            notes=deets['show_notes'],
            links=deets['show_links'],
            date=deets['show_date'],
        )

        out_dict.append(new_dict)
with open(EPISODES_MOD, 'w') as outjs:
    json.dump(out_dict, outjs, indent=4)
