from __future__ import annotations

import os
from pathlib import Path

from asyncpraw.models import Submission
import dotenv

from gurupod.core.config import get_config
from gurupod.core.logger_config import get_logger

dotenv.load_dotenv()

HERE = Path(__file__).parent
PROJECT_ROOT = HERE.parent.parent.parent
DATA_DIR = PROJECT_ROOT / os.environ.get("DATA_DIR", "data")
LOG_DIR = DATA_DIR / os.environ.get("LOG_DIR", "log")
LOG_FILENAME = LOG_DIR / os.environ.get("LOG_FILE", "gurulog.log")
LOG_PATH = LOG_DIR / LOG_FILENAME
BACKUP_RESTORE_DIR = HERE.parent / "backup_restore"
CONFIG_FILENAME = os.environ.get("CONFIG_FILE", "guruconfig.toml")
CONFIG_PATH = DATA_DIR / CONFIG_FILENAME
LOG_PROFILE = os.environ.get("LOG_PROFILE")

logger = get_logger(log_file=LOG_PATH, profile=LOG_PROFILE)

default_configs = [
    BACKUP_RESTORE_DIR / "config_local.toml",
    BACKUP_RESTORE_DIR / "config_remote.toml",
    BACKUP_RESTORE_DIR / "config_default.toml",
]

guru_conf = get_config(CONFIG_PATH, default_configs, DATA_DIR)

# reddits
SUB_TO_MONITOR = guru_conf.get("sub_to_monitor")
SUB_TO_POST = guru_conf.get("sub_to_post")
SUB_TO_WIKI = guru_conf.get("sub_to_wiki")
WIKI_TO_WRITE = guru_conf.get("wiki_page")
SUB_TO_TEST = guru_conf.get("sub_to_test")

GURU_FLAIR_ID = guru_conf.get("custom_flair")
DM_ADDRESS = guru_conf.get("dm_address")
HTML_TITLE = guru_conf.get("html_page_title")
# LOGGER_MATCH_STR = 'logger\.(info|warning|error|debug)\(\s*"Scraper \| (.+?)"\s*\)'
# Switches
RUN_EP_BOT: bool = guru_conf.get("run_ep_bot")
RUN_SUB_BOT: bool = guru_conf.get("run_sub_bot")
RUN_BACKUP_BOT: bool = guru_conf.get("run_backup_bot")

USE_PERSONAL_ACCOUNT: bool = guru_conf.get("use_personal")
WRITE_EP_TO_SUBREDDIT: bool = guru_conf.get("write_ep_to_subreddit")
UPDATE_WIKI: bool = guru_conf.get("update_wiki")
DO_FLAIR: bool = guru_conf.get("do_flair")
SKIP_OLD_THREADS: bool = guru_conf.get("skip_old_threads")
DEBUG: bool = guru_conf.get("debug")
INITIALIZE: bool = guru_conf.get("initialize")
MAX_EPISODE_IMPORT: int = int(guru_conf.get("max_import", 0))

# consts
BACKUP_SLEEP: int = guru_conf.get("backup_sleep")
EPISODE_MONITOR_SLEEP: int = guru_conf.get("episode_monitor_sleep")
MAX_SCRAPED_DUPES: int = guru_conf.get("max_scraped_dupes")

# links
MAIN_URL: str = guru_conf.get("main_url")
USER_AGENT: str = guru_conf.get("user_agent")
REDIRECT: str = guru_conf.get("redirect")

# paths
GURU_DB = DATA_DIR / guru_conf.get("db_name")
BACKUP_DIR = DATA_DIR / guru_conf.get("backup_dir")
BACKUP_JSON = BACKUP_DIR / guru_conf.get("backup_json")

# env vars
if USE_PERSONAL_ACCOUNT:
    CLIENT_ID = os.environ["PERSONAL_CLIENT_ID"]
    CLIENT_SEC = os.environ["PERSONAL_CLIENT_SEC"]
    REDDIT_TOKEN = os.environ["PERSONAL_REF_TOK"]
else:
    CLIENT_ID = os.environ["REDDIT_CLINT_ID"]
    CLIENT_SEC = os.environ["REDDIT_CLIENT_SEC"]
    REDDIT_TOKEN = os.environ["REDDIT_TOKEN"]

REDDIT_SEND_KEY = os.environ["REDDIT_SEND_KEY"]

GURU_NAME_LIST_FILE = BACKUP_RESTORE_DIR / guru_conf.get("gurus_file")

params_to_log_names = [
    "USE_PERSONAL_ACCOUNT",
    "WRITE_EP_TO_SUBREDDIT",
    "UPDATE_WIKI",
    "DO_FLAIR",
    "RUN_EP_BOT",
    "RUN_SUB_BOT",
    "RUN_BACKUP_BOT",
    "SKIP_OLD_THREADS",
    "DEBUG",
    "INITIALIZE",
]

# Create a list of tuples, each containing a parameter name and its value
params_to_log = [(param, globals()[param]) for param in params_to_log_names]


# Pass the list to your logger
def param_log_strs() -> list[str]:
    res = [f"{param}: {value}" for param, value in params_to_log if value]
    return res


class SubmissionGurus(Submission):
    def __init__(self, *args):
        super().__init__(*args)
        self.gurus = []
