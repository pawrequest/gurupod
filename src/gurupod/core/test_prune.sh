#!/bin/bash
source ./prune_backup.sh

# Function to create a single dummy backup file
create_dummy_backup() {
    local backup_dir=$1
    local date_str=$2
    touch "$backup_dir/backup-$date_str.json"
    touch "$backup_dir/gurulog-$date_str.log"
    echo "Created backup file: $backup_dir/backup-$date_str.json"
}

count_files() {
    local backup_dir=$1
    echo "$(ls -1 $backup_dir | wc -l)"
}


# Simulate daily backups for 9 weeks
for ((week=55; week>=1; week--)); do
    for ((day=7; day>=1; day--)); do
        # Calculate the date for the backup
        date_str=$(date -d "now - $((week - 1)) week - $((day - 1)) day" +%Y-%m-%d)
        echo test datestr $date_str


        # Create a backup for this date
        make_backups $date_str
        prune_all


        # Output the number of files in each directory (optional)
        echo "After $week week(s) and $day day(s):"
        echo "  Daily backups: $(count_files "${DAILY_DIR}")"
        echo "  Weekly backups: $(count_files "${WEEKLY_DIR}")"
        echo "  Monthly backups: $(count_files "${MONTHLY_DIR}")"
        echo "  Yearly backups: $(count_files "${YEARLY_DIR}")"
    done
done
