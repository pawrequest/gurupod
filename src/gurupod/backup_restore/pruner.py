import shutil
from datetime import datetime
from pathlib import Path

from loguru import logger


def prune(
    input_file: Path, day_retain=7, week_retain=4, month_retain=12, year_retain=5, debug_mode=0, backup_date=None
):
    if not input_file.exists():
        raise FileNotFoundError(f"File {input_file} does not exist")
    logger.debug("Pruning backups", bot_name="Backup")

    root_dir = input_file.parent
    intervals = {"day": day_retain, "week": week_retain, "month": month_retain, "year": year_retain}
    create_backup_dirs(root_dir, intervals)
    make_backup(input_file, root_dir, intervals, debug_mode, backup_date)
    prune_backups(root_dir, intervals)

    logger.debug("Pruning complete", bot_name="Backup")


def create_backup_dirs(root_dir: Path, intervals):
    for period in intervals:
        backup_dir = root_dir / period
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created backup directory: {backup_dir}", bot_name="Backup")


def make_backup(input_file, root_dir, intervals, debug_mode, backup_date=None):
    input_file = Path(input_file)
    root_dir = Path(root_dir)

    today = backup_date if backup_date else datetime.now().strftime("%Y-%m-%d")
    dated_filename = f"{input_file.stem}-{today}{input_file.suffix}"
    daily_file = root_dir / "day" / dated_filename

    shutil.copy(input_file, daily_file)
    logger.info(f"Backup created at {daily_file}", bot_name="Backup")

    for period in intervals:
        period_dir = root_dir / period
        if debug_mode or should_copy_to_period(period, backup_date):
            shutil.copy(daily_file, period_dir)
            logger.info(f"Copied backup to {period_dir}", bot_name="Backup")


def should_copy_to_period(period, backup_date=None):
    backup_date = datetime.strptime(backup_date, "%Y-%m-%d") if backup_date else datetime.now()
    if period == "week" and backup_date.weekday() == 0:
        return True
    if period == "month" and backup_date.day == 1:
        return True
    if period == "year" and backup_date.strftime("%j") == "001":
        return True
    return False


def prune_backups(root_dir: Path, intervals):
    for period, retention in intervals.items():
        backup_dir = root_dir / period
        all_files = sorted(backup_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)

        for file in all_files[retention:]:
            file.unlink()
            logger.info(f"Removed old backup: {file}", bot_name="Backup")


# def prune_backups(root_dir: Path, intervals):
#     for period, retention in intervals.items():
#         backup_dir = root_dir / period
#         all_files = sorted(os.listdir(backup_dir), reverse=True)
#         for file in all_files[retention:]:
#             os.remove(os.path.join(backup_dir, file))
#             print(f"Removed old backup: {file}")
