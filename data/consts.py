from __future__ import annotations

import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()

# Switches
WRITE_TO_WEB = False
SKIP_OLD_THREADS = False
# BACKUP_SLEEP = 86400
BACKUP_SLEEP = 30
EPISODE_MONITOR_SLEEP = 10
DEBUG = False
INITIALIZE = True

# links
MAIN_URL = "https://decoding-the-gurus.captivate.fm"
USER_AGENT = "Guru_Pod Wiki updater by prosodyspeaks"
REDIRECT = "http://localhost:8080"

# paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EPISODES_MD = DATA_DIR / "episodes.md"
GURU_DB = DATA_DIR / "guru.db"
BACKUP_JSON = DATA_DIR / "db_backup.json"

# strings
GURU_SUB = "DecodingTheGurus"
TEST_SUB = "test"
EPISODES_WIKI = "episodes"
TEST_WIKI = "gurus"
EPISODE_PAGE_TITLE = "Decoding The Gurus Episodes"
SUB_IN_USE = TEST_SUB

# env vars
PROSODY_CLIENT_ID = os.environ["PROSODY_CLIENT_ID"]
PROSODY_CLIENT_SEC = os.environ["PROSODY_CLIENT_SEC"]
PROSODY_REF_TOK = os.environ["PROSODY_REF_TOK"]
# REDDIT_CLIENT_ID = os.environ["DTG_CLIENT_ID"]
# REDDIT_CLIENT_SEC = os.environ["DTG_CLIENT_SEC"]
# REDDIT_REF_TOK = os.environ["DTG_TOKEN"]
REDDIT_SEND_KEY = os.environ["REDDIT_SEND_KEY"]
GURU_FLAIR_ID = os.environ.get("CUSTOM_FLAIR_ID")
MONITOR_SUB = os.environ.get("RUN_SUB_BOT", False)
