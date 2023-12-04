import os
from pathlib import Path

# links
MAIN_URL = "https://decoding-the-gurus.captivate.fm"
USER_AGENT = "Guru_Pod Wiki updater by prosodyspeaks"
REDIRECT = "http://localhost:8080"

# paths
folder = Path(__file__).parent
EPISODES_MD = folder / "episodes.md"
EPISODES_JSON = folder / "episodes.json"
EPISODES_HTML = folder / 'episodes.html'

# strings
SUBRED = 'DecodingTheGurus'
WIKINAME = "episodes"
# WIKINAME = "gurus"


# env vars
REDDIT_USER = os.environ['REDDIT_USER']
REDDIT_PASS = os.environ['REDDIT_PASS']
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SEC = os.environ['REDDIT_CLIENT_SEC']
REDDIT_REF_TOK = os.environ['REDDIT_REF_TOK']
