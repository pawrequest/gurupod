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
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EPISODES_MD = DATA_DIR / "episodes.md"
EPISODES_JSON = DATA_DIR / "episodes.json"
EPISODES_MOD = DATA_DIR / "episodes_mod.json"
EPISODES_HTML = DATA_DIR / "episodes.html"
GURU_DB = DATA_DIR / "guru.db"

# strings
GURU_SUB = "DecodingTheGurus"
TEST_SUB = "test"
EPISODES_WIKI = "episodes"
TEST_WIKI = "gurus"
EPISODE_PAGE_TITLE = "Decoding The Gurus Episodes"


# env vars
REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SEC = os.environ["REDDIT_CLIENT_SEC"]
REDDIT_REF_TOK = os.environ["REDDIT_REF_TOK"]
REDDIT_SEND_KEY = os.environ["REDDIT_SEND_KEY"]

GURU_FLAIR_ID = "f0c29d96-93e4-11ee-bdde-e666ed3aa602"
