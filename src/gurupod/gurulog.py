from pathlib import Path

from loguru import logger as _logger
from loguru._logger import Logger

log_file_loc = Path(__file__).parent.parent.parent / "data" / "logs" / "gurulog.log"
_logger.add(log_file_loc, rotation="1 day", delay=True)


def get_logger() -> Logger:
    return _logger
