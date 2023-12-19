import pytest
from loguru import logger

logger.add('test.log')

@pytest.mark.asyncio
async def test_log():
    logger.info("test")


def test_re():
    import re
    with open("test.log", "r") as f:
        LOG1 = f.readline()
    pat_xml = r"^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\s)\|(\s[A-Z]*\s*)\|(\s.+:.+:\d+\s-\s.*)$"
    match = re.match(pat_xml, LOG1)

    assert match
    print("Match found!")
    print("Groups:", match.groups())
