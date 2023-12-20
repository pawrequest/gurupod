import re

import pytest
from gurupod.gurulog import logger
logger.remove()
from gurupod.gurulog import log_file_loc

@pytest.mark.asyncio
async def test_log_loc():
    ...
    assert log_file_loc == "../src/data/logs/gurulog.log"


@pytest.mark.asyncio
async def test_log(tmp_path):
    test_loc = tmp_path / "test.log"
    logger.add(test_loc)
    logger.info("test")
    logged_line = 18
    with open(test_loc, "r") as f:
        LOG1 = f.readline()
    pat_xml = r"^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\s)\|(\s[A-Z]*\s*)\|(\s.+:.+:\d+\s-\s.*)$"
    match = re.match(pat_xml, LOG1)

    assert match
    assert match.string.endswith(f' | INFO     | tests.test_log:test_log:{logged_line} - test\n')




