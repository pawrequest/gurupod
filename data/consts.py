from __future__ import annotations

import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()
# strings
GURU_SUB = "DecodingTheGurus"
TEST_SUB = "test"
EPISODES_WIKI = "episodes"
TEST_WIKI = "gurus"
EPISODE_PAGE_TITLE = "Decoding The Gurus Episodes"

# Switches
USE_PERSONAL = True
WRITE_EP_TO_SUBREDDIT = False
DO_FLAIR = False
SKIP_OLD_THREADS = False
BACKUP_SLEEP = 24 * 60 * 60
EPISODE_MONITOR_SLEEP = 60 * 10
DEBUG = False
INITIALIZE = True
RUN_EP_BOT = True
RUN_SUB_BOT = True
RUN_BACKUP_BOT = True
SUB_IN_USE = TEST_SUB
READ_SUB = GURU_SUB
WRITE_SUB = TEST_SUB
# SUB_IN_USE = GURU_SUB
MAX_SCRAPED_DUPES = 3


# links
MAIN_URL = "https://decoding-the-gurus.captivate.fm"
USER_AGENT = "DecodeTheBot v0.1"
REDIRECT = "http://localhost:8080"

# paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EPISODES_MD = DATA_DIR / "episodes.md"
GURU_DB = DATA_DIR / "guru.db"
BACKUP_JSON = DATA_DIR / "db_backup.json"


# env vars
if USE_PERSONAL:
    CLIENT_ID = os.environ["PROSODY_CLIENT_ID"]
    CLIENT_SEC = os.environ["PROSODY_CLIENT_SEC"]
    REDDIT_TOKEN = os.environ["PROSODY_REF_TOK"]
else:
    CLIENT_ID = os.environ["DTG_CLIENT_ID"]
    CLIENT_SEC = os.environ["DTG_CLIENT_SEC"]
    REDDIT_TOKEN = os.environ["DTG_TOKEN"]

REDDIT_SEND_KEY = os.environ["REDDIT_SEND_KEY"]
GURU_FLAIR_ID = os.environ.get("CUSTOM_FLAIR_ID")
