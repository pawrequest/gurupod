import re
import json
from pprint import pprint

from data.consts import EPISODES_JSON, EPISODES_MOD
from gurunames import GURUS, NEW
NEW_EPISODES_JSON = 'new_episodes.json'


def change1():
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


def add_gurus(episodes_json=EPISODES_JSON):
    with open(episodes_json, 'r') as f:
        episodes = json.load(f)

    for episode in episodes:
        title = episode['name']
        # Find two or three-word strings with capitalization
        gurus = re.findall(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})', title)
        episode['gurus'] = gurus

    with open(NEW_EPISODES_JSON, 'w') as f:
        json.dump(episodes, f, indent=4)


def get_gurus():
    with open(NEW_EPISODES_JSON) as f:
        episodes = json.load(f)
        gurus = {
            guru
            for ep in episodes
            for guru in ep['gurus']
        }

    with open('gurulist.txt', 'w') as f:
        f.write('\n'.join(sorted(gurus)))



def combo():
    all_gurus = set(GURUS + NEW)
    with open('gurulist.txt', 'w', encoding='UTF-8') as f:
        f.write('\n'.join(sorted(all_gurus)))


if __name__ == '__main__':
    combo()
