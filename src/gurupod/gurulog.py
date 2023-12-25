from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence, TYPE_CHECKING

from loguru import logger as _logger

if TYPE_CHECKING:
    from loguru._logger import Logger
    from gurupod.models.responses import EP_VAR

log_file_loc = Path(__file__).parent.parent.parent / "data" / "logs" / "gurulog.log"
_logger.remove()
_logger.add(log_file_loc, rotation="1 day", delay=True)
_logger.add(sys.stdout, level="DEBUG")


def get_logger() -> Logger:
    return _logger


def log_urls(urls: Sequence[str], msg: str = None):
    if not urls:
        return
    if msg:
        _logger.info(msg)
        return
    msg += f"\nFound {len(urls)} urls:\n"
    msg += "\n".join("\t" + _ for _ in urls[:5])
    if len(urls) > 5:
        msg += " \n\t... more ..."
    _logger.info(msg)


def log_episodes(eps: Sequence[EP_VAR], calling_func=None, msg: str = ""):
    msg = msg + f" {len(eps)} Episodes:"
    if calling_func:
        msg = f"Logger called by {calling_func.__name__}:\n\t{msg}\n"
    if not eps:
        return
    msg += episode_log_string(eps)
    _logger.info(msg)


def episode_log_string(eps: Sequence[EP_VAR]) -> str:
    msg = ""
    try:
        msg += "\n".join(f"\t {_.date.date()} - {_.title}" for _ in eps[:3])
    except AttributeError:
        try:
            msg += "\n".join("\t" + _.url for _ in eps[:3])
        except AttributeError:
            raise TypeError(f"Expected Episode, got {type(eps[0])}")
    if len(eps) == 4:
        fth = eps[3]
        msg += f"\n\t {fth.date.date()} - {fth.title}"
    elif len(eps) > 4:
        to_log = min([2, abs(len(eps) - 4)])
        msg += " \n\t...\n"
        msg += "\n".join(f"\t {_.date.date()} - {_.title}" for _ in eps[-to_log:])
    if len(eps) > 5:
        msg += " \n\t... more ..."
    return msg
