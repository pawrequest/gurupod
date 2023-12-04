import json
from models import Episode

# new_episodes = {}
# with open("episodes.json", "r") as f:
#     episodes_dict = dict(json.load(f))
#     for episode, details in episodes_dict.items():
#         show_name = episode
#         show_date = details['Date']
#         show_url = details['URL']
#         show_notes = details['Show Notes']
#         show_links = details['Show Links']
#         new_episodes[show_name] = {'show_date' : show_date, 'show_url' : show_url, 'show_notes':show_notes, 'show_links': show_links}
#
# with open("new_episodes.json", 'w') as f:
#     json.dump(new_episodes, f)

episodes = []
with open("../../data/new_episodes.json", 'r') as f:
    episodes_dict = json.load(f)
    for episode, details in episodes_dict.items():
        episode_o = Episode(episode, show_date=details['show_date'], show_url=details['show_url'],
                            show_notes=details['show_notes'], show_links=details['show_links'])
        episodes.append(episode_o)
...
print (episodes)


