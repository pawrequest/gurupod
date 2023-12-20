from loguru import logger
log_file_loc = "../src/data/logs/gurulog.log"
logger.add(log_file_loc, rotation="1 day", delay=True)
