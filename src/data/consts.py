from __future__ import annotations

import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()
# links
MAIN_URL = "https://decoding-the-gurus.captivate.fm"
USER_AGENT = "Guru_Pod Wiki updater by prosodyspeaks"
REDIRECT = "http://localhost:8080"

# paths
folder = Path(__file__).parent
EPISODES_MD = folder / "episodes.md"
EPISODES_JSON = folder / "episodes.json"
NEWEPS_JSON = folder / 'episodes2.json'
EPISODES_HTML = folder / 'episodes.html'
GURU_DB = folder / 'guru.db'

# strings
DTG_SUB = 'DecodingTheGurus'
EPISODES_WIKI = "episodes"
# WIKINAME = "gurus"


# env vars
REDDIT_USER = os.environ['REDDIT_USER']
REDDIT_PASS = os.environ['REDDIT_PASS']
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SEC = os.environ['REDDIT_CLIENT_SEC']
REDDIT_REF_TOK = os.environ['REDDIT_REF_TOK']
REDDIT_SUB_KEY = os.environ['REDDIT_SUB_KEY']
PAGE_TITLE = 'Decoding The Gurus Episodes'
GURUS = {'________________________________', '_______________________________'}
