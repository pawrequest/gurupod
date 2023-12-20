import os.path
from pathlib import Path

from loguru import logger
# log_file_loc = "../../src/data/logs/gurulog.log"
log_file_loc = Path(__file__).parent.parent.parent / 'data' / 'logs' / 'gurulog.log'

logger.add(log_file_loc, rotation="1 day", delay=True)
logger.info(f'Starting logger {log_file_loc}')
