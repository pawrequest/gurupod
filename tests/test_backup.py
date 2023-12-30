import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from gurupod.backup_restore.pruner import prune


def test_backup_pruning():
    # Create a temporary directory and a test file
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "testfile.txt"
        with open(test_file, "w") as f:
            f.write("Test content")

        # Simulate 9 weeks of backups
        for week in range(9):
            for day in range(7):
                backup_date = (datetime.now() + timedelta(weeks=week, days=day)).strftime("%Y-%m-%d")
                prune(test_file, day_retain=7, week_retain=4, month_retain=12, year_retain=5, backup_date=backup_date)

        # Check the number of backups in each directory
        for period, expected_count in [("day", 7), ("week", 4), ("month", 12), ("year", 5)]:
            backup_dir = os.path.join(tmp_dir, period)
            actual_count = len(os.listdir(backup_dir))
            assert (
                actual_count <= expected_count
            ), f"Too many backups in {period} directory: {actual_count} (expected: {expected_count})"

        print("All tests passed!")
