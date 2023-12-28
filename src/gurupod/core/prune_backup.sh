#!/bin/bash

##!/bin/bash
#ROOT_DIR=$(dirname $(dirname $(dirname $(dirname $(realpath $0 )))))
#echo "ROOT_DIR = $ROOT_DIR"
#
## Correctly set the BACKUP_DIR path
#BACKUP_DIR="${ROOT_DIR}/data/backup/"
#echo TESTPRUNE "BACKUP_DIR = $BACKUP_DIR"
#
## Backup directories
#DAILY_DIR="${BACKUP_DIR}"
#WEEKLY_DIR="${BACKUP_DIR}week"
#MONTHLY_DIR="${BACKUP_DIR}month"
#YEARLY_DIR="${BACKUP_DIR}year"
#
#echo "PRUNE Resolved daily backup directory: $DAILY_DIR"
#echo "PRUNE Resolved weekly backup directory: $WEEKLY_DIR"
#echo "PRUNE Resolved monthly backup directory: $MONTHLY_DIR"
#echo "PRUNE Resolved yearly backup directory: $YEARLY_DIR"
## Backup retention counts
#DAILY_RETENTION=7    # e.g., 7 for a week
#WEEKLY_RETENTION=4   # e.g., 4 for a month
#MONTHLY_RETENTION=12 # e.g., 12 for a year
#YEARLY_RETENTION=5   # e.g., 5 years
#
## Function to prune backups
#prune_backups() {
#    local backup_dir=$1
#    local retention=$2
#    # Delete old backups, keeping the $retention most recent
#    ls -tp "$backup_dir" | grep -v '/$' | tail -n +$(($retention + 1)) | xargs -I {} rm -- $backup_dir/{}
#}
#
## Copy backup to weekly/monthly/yearly if it's the first day of the week/month/year
#today=$(date +%Y-%m-%d)
#day_of_week=$(date +%u)
#day_of_month=$(date +%d)
#day_of_year=$(date +%j)
#
#if [ "$day_of_week" -eq 1 ]; then
#    cp "$DAILY_DIR/backup-$today.json" "$WEEKLY_DIR/"
#fi
#if [ "$day_of_month" -eq 1 ]; then
#    cp "$DAILY_DIR/backup-$today.json" "$MONTHLY_DIR/"
#fi
#if [ "$day_of_year" -eq 1 ]; then
#    cp "$DAILY_DIR/backup-$today.json" "$YEARLY_DIR/"
#fi
#
## Prune old backups
#prune_backups "$DAILY_DIR" $DAILY_RETENTION
#prune_backups "$WEEKLY_DIR" $WEEKLY_RETENTION
#prune_backups "$MONTHLY_DIR" $MONTHLY_RETENTION
#prune_backups "$YEARLY_DIR" $YEARLY_RETENTION

## Debug mode flag (set to 1 to enable debug mode)
#DEBUG_MODE=1
#
#
#ROOT_DIR=$(dirname $(dirname $(dirname $(dirname $(realpath $0 )))))
#echo "ROOT_DIR = $ROOT_DIR"
#
## Correctly set the BACKUP_DIR path
#BACKUP_DIR="${ROOT_DIR}/data/backup/"
#echo "PRUNE BACKUP_DIR = $BACKUP_DIR"
#
## Backup directories
#DAILY_DIR="${BACKUP_DIR}day"
#WEEKLY_DIR="${BACKUP_DIR}week"
#MONTHLY_DIR="${BACKUP_DIR}month"
#YEARLY_DIR="${BACKUP_DIR}year"
#
## Create directories if they do not exist
#mkdir -p "$DAILY_DIR" "$WEEKLY_DIR" "$MONTHLY_DIR" "$YEARLY_DIR"
#
## Backup retention counts
#DAILY_RETENTION=7
#WEEKLY_RETENTION=4
#MONTHLY_RETENTION=12
#YEARLY_RETENTION=5
#
#
#
## Function to prune backups
#prune_backups() {
#    local backup_dir=$1
#    local retention=$2
#    ls -tp "$backup_dir" | grep -v '/$' | tail -n +$(($retention + 1)) | xargs -I {} rm -- "$backup_dir/{}"
#}
#
## Find the most recent backup file
#latest_backup=$(ls -t "$DAILY_DIR" | head -n 1)
#echo "Latest backup file: $latest_backup"
#
## Copy the latest backup file to weekly/monthly/yearly directories
#if [ "$DEBUG_MODE" -eq 1 ] || [ "$(date +%u)" -eq 1 ]; then
#    cp "$DAILY_DIR/$latest_backup" "$WEEKLY_DIR/"
#fi
#if [ "$DEBUG_MODE" -eq 1 ] || [ "$(date +%d)" -eq 1 ]; then
#    cp "$DAILY_DIR/$latest_backup" "$MONTHLY_DIR/"
#fi
#if [ "$DEBUG_MODE" -eq 1 ] || [ "$(date +%j)" -eq 1 ]; then
#    cp "$DAILY_DIR/$latest_backup" "$YEARLY_DIR/"
#fi
#
## Prune old backups
#prune_backups "$DAILY_DIR" $DAILY_RETENTION
#prune_backups "$WEEKLY_DIR" $WEEKLY_RETENTION
#prune_backups "$MONTHLY_DIR" $MONTHLY_RETENTION
#prune_backups "$YEARLY_DIR" $YEARLY_RETENTION



# Debug mode flag (set to 1 to enable debug mode, 0 to disable)
DEBUG_MODE=1

# Define root directory
ROOT_DIR=$(dirname $(dirname $(dirname $(dirname $(realpath $0 )))))
echo "ROOT_DIR = $ROOT_DIR"

# Define backup directory
BACKUP_DIR="${ROOT_DIR}/data/backup/"
echo "PRUNE BACKUP_DIR = $BACKUP_DIR"

# Backup directories
DAILY_DIR="${BACKUP_DIR}day/"
WEEKLY_DIR="${BACKUP_DIR}week/"
MONTHLY_DIR="${BACKUP_DIR}month/"
YEARLY_DIR="${BACKUP_DIR}year/"

# Create backup directories if they don't exist
mkdir -p "$DAILY_DIR" "$WEEKLY_DIR" "$MONTHLY_DIR" "$YEARLY_DIR"

# Backup retention counts
DAILY_RETENTION=7
WEEKLY_RETENTION=4
MONTHLY_RETENTION=12
YEARLY_RETENTION=5

# Function to prune backups
prune_backups() {
    local backup_dir=$1
    local retention=$2
    ls -tp "$backup_dir" | grep -v '/$' | tail -n +$(($retention + 1)) | xargs -I {} rm -- "$backup_dir/{}"
}

# Rename the main backup file with the current date
today=$(date +%Y-%m-%d)
mv "${BACKUP_DIR}db_backup.json" "${DAILY_DIR}backup-${today}.json"

# Copy the latest backup file to weekly/monthly/yearly directories
latest_backup=$(ls -t "$DAILY_DIR" | head -n 1)

if [ "$DEBUG_MODE" -eq 1 ] || [ "$(date +%u)" -eq 1 ]; then
    cp "${DAILY_DIR}${latest_backup}" "${WEEKLY_DIR}"
fi
if [ "$DEBUG_MODE" -eq 1 ] || [ "$(date +%d)" -eq 1 ]; then
    cp "${DAILY_DIR}${latest_backup}" "${MONTHLY_DIR}"
fi
if [ "$DEBUG_MODE" -eq 1 ] || [ "$(date +%j)" -eq 1 ]; then
    cp "${DAILY_DIR}${latest_backup}" "${YEARLY_DIR}"
fi

# Prune old backups
prune_backups "$DAILY_DIR" $DAILY_RETENTION
prune_backups "$WEEKLY_DIR" $WEEKLY_RETENTION
prune_backups "$MONTHLY_DIR" $MONTHLY_RETENTION
prune_backups "$YEARLY_DIR" $YEARLY_RETENTION
