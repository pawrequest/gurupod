import os
import shutil
from datetime import datetime


def create_backup_dirs(root_dir, intervals):
    for period in intervals:
        backup_dir = os.path.join(root_dir, period)
        os.makedirs(backup_dir, exist_ok=True)
        print(f"Created backup directory: {backup_dir}")


def make_backup(input_file, root_dir, intervals, debug_mode, backup_date=None):
    today = backup_date if backup_date else datetime.now().strftime("%Y-%m-%d")

    extension = os.path.splitext(input_file)[1]
    filename_only = os.path.splitext(os.path.basename(input_file))[0]
    dated_filename = f"{filename_only}-{today}{extension}"
    daily_file = os.path.join(root_dir, "day", dated_filename)
    shutil.copy(input_file, daily_file)
    print(f"Backup created at {daily_file}")

    for period in intervals:
        period_dir = os.path.join(root_dir, period)
        if debug_mode or should_copy_to_period(period):
            shutil.copy(daily_file, period_dir)
            print(f"Copied backup to {period_dir}")


def should_copy_to_period(period):
    today = datetime.now()
    if period == "week" and today.weekday() == 0:
        return True
    if period == "month" and today.day == 1:
        return True
    if period == "year" and today.strftime("%j") == "001":
        return True
    return False


def prune_backups(root_dir, intervals):
    for period, retention in intervals.items():
        backup_dir = os.path.join(root_dir, period)
        all_files = sorted(os.listdir(backup_dir), reverse=True)
        for file in all_files[retention:]:
            os.remove(os.path.join(backup_dir, file))
            print(f"Removed old backup: {file}")


def prune(input_file, day_retain=7, week_retain=4, month_retain=12, year_retain=5, debug_mode=0, backup_date=None):
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"File {input_file} does not exist")

    root_dir = os.path.dirname(input_file)
    intervals = {"day": day_retain, "week": week_retain, "month": month_retain, "year": year_retain}

    create_backup_dirs(root_dir, intervals)
    make_backup(input_file, root_dir, intervals, debug_mode, backup_date)
    prune_backups(root_dir, intervals)
