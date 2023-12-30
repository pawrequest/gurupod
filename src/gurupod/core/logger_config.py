from __future__ import annotations

import sys
from typing import Literal, TYPE_CHECKING

from loguru import logger as _logger

if TYPE_CHECKING:
    from loguru import logger


def get_logger(log_file, profile: Literal["local", "remote", "default"] = None) -> logger:
    if profile == "local":
        _logger.info("Using local log profile")
        terminal_format = terminal_format_local
    elif profile == "remote":
        _logger.info("Using remote log profile")
        terminal_format = terminal_format_remote
    elif profile is None:
        _logger.info("Using default log profile (remote)")
        terminal_format = terminal_format_remote
    else:
        raise ValueError(f"Invalid profile: {profile}")

    _logger.remove()

    _logger.add(log_file, rotation="1 day", delay=True)
    _logger.add(sys.stdout, level="DEBUG", format=terminal_format)

    return _logger


BOT_COLOR = {
    "Scraper": "cyan",
    "Monitor": "green",
    "BackupBot": "magenta",
}


def terminal_format_local(record):
    bot_name = record["extra"].get("bot_name", "General")
    bot_name = f"{bot_name:<9}"
    bot_colour = BOT_COLOR.get(bot_name, "white")
    max_length = 80
    file_txt = f"{record['file'].path}:{record['line']}"

    if len(file_txt) > max_length:
        file_txt = file_txt[:max_length]

    # clickable link only works at start of line
    return f"{file_txt:<{max_length}} | <lvl>{record['level']: <7} | {coloured(bot_name, bot_colour)} | {record['message']}</lvl>\n"


def coloured(msg: str, colour: str) -> str:
    return f"<{colour}>{msg}</{colour}>"


def terminal_format_remote(record):
    bot_name = record["extra"].get("bot_name", "General")
    bot_name = f"{bot_name:<9}"
    bot_colour = BOT_COLOR.get(bot_name, "white")

    file_line = f"{record['file']}:{record['line']}- {record['function']}()"
    bot_says = f"<bold>{coloured(bot_name, bot_colour):<9} </bold> | {coloured(record['message'], bot_colour)}"

    return f"<lvl>{record['level']: <7} </lvl>| {bot_says} | {file_line}\n"
