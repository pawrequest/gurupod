import json
import re

from data.consts import EPISODES_JSON, EPISODES_MOD

NEW_EPISODES_JSON = "new_episodes.json"


def change1():
    with open(EPISODES_JSON) as injs:
        eps = json.load(injs)
        out_ = [
            dict(
                title=deets["name"],
                url=deets["url"],
                notes=deets["notes"],
                links=deets["links"],
                date=deets["date"],
            )
            for deets in eps
        ]

    with open(EPISODES_MOD, "w") as outjs:
        json.dump(out_, outjs, indent=4)


def add_gurus(episodes_json=EPISODES_JSON):
    with open(episodes_json, "r") as f:
        episodes = json.load(f)

    for episode in episodes:
        title = episode["title"]
        # Find two or three-word strings with capitalization
        gurus = extract_gurus_from_string(title)
        episode["gurus"] = gurus

    with open(NEW_EPISODES_JSON, "w") as f:
        json.dump(episodes, f, indent=4)


def extract_gurus_from_string(string_):
    # Find two or three-word strings with capitalization
    gurus = re.findall(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})", string_)
    return gurus


if __name__ == "__main__":
    change1()
