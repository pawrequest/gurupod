#!/bin/bash
##!/bin/bash
#
#
#ROOT_DIR=$(dirname $(dirname $(dirname $(dirname $(realpath $0 )))))
#echo "ROOT_DIR = $ROOT_DIR"
#
## Correctly set the BACKUP_DIR path
#BACKUP_DIR="${ROOT_DIR}/data/backup/"
#echo "TESTPRUNE BACKUP_DIR = $BACKUP_DIR"
#
## Backup directories
#DAILY_DIR="${BACKUP_DIR}day"
#WEEKLY_DIR="${BACKUP_DIR}week"
#MONTHLY_DIR="${BACKUP_DIR}month"
#YEARLY_DIR="${BACKUP_DIR}year"
#
#echo "Resolved daily backup directory: $DAILY_DIR"
#echo "Resolved weekly backup directory: $WEEKLY_DIR"
#echo "Resolved monthly backup directory: $MONTHLY_DIR"
#echo "Resolved yearly backup directory: $YEARLY_DIR"
#
## Path to your backup rotation script
#BACKUP_ROTATION_SCRIPT="./prune_backup.sh"
#
## Function to create dummy backup files
#create_dummy_backups() {
#    local backup_dir=$1
#    local num_files=$2
#    local start_date=$(date +%s) # Current timestamp
#
#    for ((i=0; i<num_files; i++)); do
#        # Create a file with a timestamp in the past
#        local date_str=$(date -d "@$((start_date - i * 86400))" +%Y-%m-%d)
#        touch "$backup_dir/backup-$date_str.json"
#    done
#}
#
## Function to check the number of files in a directory
#count_files() {
#    local backup_dir=$1
#    echo $(ls -1 $backup_dir | wc -l)
#}
#
## Create 8 dummy files in the daily backup folder
#create_dummy_backups $DAILY_DIR 8
#
## Run the backup rotation script
#bash $BACKUP_ROTATION_SCRIPT
#
## Output the number of files in each directory
#echo "Daily backups: $(count_files $DAILY_DIR)"
#echo "Weekly backups: $(count_files $WEEKLY_DIR)"
#echo "Monthly backups: $(count_files $MONTHLY_DIR)"
#echo "Yearly backups: $(count_files $YEARLY_DIR)"




ROOT_DIR=$(dirname $(dirname $(dirname $(dirname $(realpath $0 )))))
echo "ROOT_DIR = $ROOT_DIR"

# Correctly set the BACKUP_DIR path
BACKUP_DIR="${ROOT_DIR}/data/backup/"
echo "TESTPRUNE BACKUP_DIR = $BACKUP_DIR"

# Backup directories
DAILY_DIR="${BACKUP_DIR}day"
WEEKLY_DIR="${BACKUP_DIR}week"
MONTHLY_DIR="${BACKUP_DIR}month"
YEARLY_DIR="${BACKUP_DIR}year"

# Create directories if they do not exist
mkdir -p "$DAILY_DIR" "$WEEKLY_DIR" "$MONTHLY_DIR" "$YEARLY_DIR"

# Path to your backup rotation script
BACKUP_ROTATION_SCRIPT="./prune_backup.sh"

# Function to create a single dummy backup file
create_dummy_backup() {
    local backup_dir=$1
    local date_str=$2
    touch "$backup_dir/backup-$date_str.json"
}

# Function to check the number of files in a directory
count_files() {
    local backup_dir=$1
    echo $(ls -1 $backup_dir | wc -l)
}

# Simulate daily backups for 9 weeks
for ((week=1; week<=9; week++)); do
    for ((day=1; day<=7; day++)); do
        # Calculate the date for the backup
        date_str=$(date -d "now - $((week - 1)) week - $((day - 1)) day" +%Y-%m-%d)

        # Create a backup for this date
        create_dummy_backup $DAILY_DIR $date_str

        # Run the backup rotation script
        bash $BACKUP_ROTATION_SCRIPT

        # Output the number of files in each directory (optional)
        echo "After $week week(s) and $day day(s):"
        echo "  Daily backups: $(count_files $DAILY_DIR)"
        echo "  Weekly backups: $(count_files $WEEKLY_DIR)"
        echo "  Monthly backups: $(count_files $MONTHLY_DIR)"
        echo "  Yearly backups: $(count_files $YEARLY_DIR)"
    done
done
