import re

import pytest

from data.consts import PROJECT_ROOT
from gurupod.gurulog import log_file_loc
from tests.conftest import override_logger


@pytest.mark.asyncio
async def test_log_loc():
    logpath = PROJECT_ROOT / "data" / "logs" / "gurulog.log"
    assert log_file_loc == logpath


@pytest.mark.asyncio
async def test_log(tmp_path, test_logger):
    test_logger.info("test")


@pytest.mark.asyncio
async def test_log(tmp_path):
    logger = override_logger()
    test_loc = tmp_path / "test.log"
    logger.add(test_loc)
    logger.info("test")
    logged_line = 26
    with open(test_loc, "r") as f:
        LOG1 = f.readline()
    pat_xml = r"^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\s)\|(\s[A-Z]*\s*)\|(\s.+:.+:\d+\s-\s.*)$"
    match = re.match(pat_xml, LOG1)

    assert match
    assert match.string.endswith(
        f" | INFO     | tests.test_log:test_log:{logged_line} - test\n"
    )
