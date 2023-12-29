from __future__ import annotations

import inspect
import sys
from typing import Sequence, TYPE_CHECKING

from loguru import logger as _logger

from data.consts import LOG_FILE

if TYPE_CHECKING:
    from loguru._logger import Logger
    from gurupod.models.responses import EP_OR_BASE_VAR


def custom_format(record):
    max_length = 90
    file_line = f"{record['file'].path}:{record['line']} - {record['function']}:"

    if len(file_line) > max_length:
        file_line = file_line[:max_length]

    return f"{file_line:<{max_length}} <lvl>{record['level']: <7}  {record['message']}</lvl>\n"


_logger.remove()
clickable = "{file.path}:{line}"
format_ = clickable + " <lvl>{level: <8} {function}</lvl>: {message}"

_logger.add(LOG_FILE, rotation="1 day", delay=True)
_logger.add(sys.stdout, level="DEBUG", format=custom_format)


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


def log_episodes(eps: Sequence[EP_OR_BASE_VAR], calling_func=None, msg: str = ""):
    if not eps:
        return
    if calling_func:
        calling_f = calling_func.__name__
    else:
        calling_f = f"{inspect.stack()[1].function} INSPECTED, YOU SHOULD PROVIDE THE FUNC"

    new_msg = f"{calling_f} logging:\n\t\t{msg} {len(eps)} Episodes:\n"
    new_msg += episode_log_msg(eps)
    _logger.info(new_msg)


def episode_log_msg(eps: Sequence[EP_OR_BASE_VAR]) -> str:
    msg = ""
    try:
        msg += "\n".join(f"\t\t <green>{_.date.date()}</green> - <bold><cyan>{_.title}</cyan></bold>" for _ in eps[:3])
    except AttributeError:
        try:
            msg += "\n".join("\t\t" + _.url for _ in eps[:3])
        except AttributeError:
            raise TypeError(f"Expected Episode, got {type(eps[0])}")
    if len(eps) == 4:
        fth = eps[3]
        msg += f"\n\t {fth.date.date()} - {fth.title}"
    elif len(eps) > 4:
        to_log = min([2, abs(len(eps) - 4)])
        msg += " \n\t...\n"
        msg += "\n".join(f"\t\t {_.date.date()} - {_.title}" for _ in eps[-to_log:])
    if len(eps) > 5:
        msg += " \n\t... more ..."
    return msg
