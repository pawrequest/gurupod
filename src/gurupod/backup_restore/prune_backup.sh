#!/bin/bash
# This script creates daily, weekly, monthly, and yearly backups of a file
# It should be run daily, and will create a backup for the current day
# If it's the first day of the week, month, or year, it will also create a backup for that period
# It will then delete old backups, keeping days, weeks, months, years as defined in args, or 7, 4, 12, and 5 by default

DEBUG_MODE=0 # do stuff even if not the right day
INPUT_FILE=$1
TODAY=${2:-$(date +%Y-%m-%d)}
DAY_RETAIN=${3:-7}
WEEK_RETAIN=${4:-4}
MONTH_RETAIN=${5:-12}
YEAR_RETAIN=${6:-5}

# if input file doesnt exist:
if [ ! -f "$INPUT_FILE" ]; then
    echo "File $INPUT_FILE does not exist"
    exit 1
fi


ROOT_DIR=$(dirname "$INPUT_FILE")

# how many backups to keep for each period
# also defines folder names
declare -A INTERVAL
INTERVAL["day"]=$DAY_RETAIN
INTERVAL["week"]=$WEEK_RETAIN
INTERVAL["month"]=$MONTH_RETAIN
INTERVAL["year"]=$YEAR_RETAIN

EXTENSION="${INPUT_FILE##*.}"
FILENAME_ONLY="$(basename "$INPUT_FILE" ."$EXTENSION")"
DATED_FILENAME="${FILENAME_ONLY}-${TODAY}.${EXTENSION}"



echo "INPUT_FILE = $INPUT_FILE"
check_dirs_exist() {
    for PERIOD in "${!INTERVAL[@]}"; do
        local BACKUP_DIR="${ROOT_DIR}/${PERIOD}"
        echo "Checking if $BACKUP_DIR exists"
        if [ ! -d "$BACKUP_DIR" ]; then
            return 1 # Return 1 if any directory doesn't exist
        fi
    done
    return 0
}


checkem(){
  if ! check_dirs_exist; then
      echo "One or more backup directories do not exist. Do you want to create them? (y/n)"
      read answer
      if [[ $answer =~ ^[Yy]$ ]]; then
          for PERIOD in "${!INTERVAL[@]}"; do
              local BACKUP_DIR="${ROOT_DIR}/${PERIOD}"
              mkdir -p "$BACKUP_DIR"
              echo "Created backup directory: $BACKUP_DIR"
          done
      else
          echo "Aborting..."
          exit 1
      fi
  fi
}

make_backups() {
  # append today's date to the filename then copy it to the daily backup directory
  # if it's the first day of the week, month, or year, also copy it to the respective directory
  local daily_file="${ROOT_DIR}/day/${DATED_FILENAME}"
  cp "$INPUT_FILE" "$daily_file"
  echo "Backup created at $daily_file"

  for PERIOD in "${!INTERVAL[@]}"; do
    # first day of week, month, year, we copy the daily backup to the respective period directory
    local period_dir="${ROOT_DIR}/${PERIOD}"
    if [ "$DEBUG_MODE" -eq 1 ] ||
      ([ "$PERIOD" = "week" ] && [ "$(date +%u)" -eq 1 ]) ||
      ([ "$PERIOD" = "month" ] && [ "$(date +%d)" -eq 1 ]) ||
      ([ "$PERIOD" = "year" ] && [ "$(date +%j)" -eq 1 ]); then
        cp "$daily_file" "$period_dir/"
        echo "Copied backup to $period_dir"
    fi
  done
}

#prune_backups() {
#  local backup_dir=$1
#  local retention=${INTERVAL[$(basename "$backup_dir")]}
#  ls -tp "$backup_dir" | grep -v '/$' | grep "$FILENAME_ONLY" | tail -n +$(($retention + 1)) | xargs -I {} rm -- "$backup_dir/{}"
#  echo "Pruned backups in $backup_dir for $FILENAME_ONLY"
#}
prune_backups() {
  # delete old backups, keep as many as defined in INTERVAL for each period
    local backup_dir=$1
    local retention=${INTERVAL[$(basename "$backup_dir")]}
    local count=0

    for file in "$backup_dir/$FILENAME_ONLY"*; do
        if [ -f "$file" ]; then
            ((count++))
            if [ $count -gt $retention ]; then
                echo "Removing old backup: $file"
                rm -- "$file"
            fi
        fi
    done
}
prune_all() {
  for PERIOD in "${!INTERVAL[@]}"; do
    local period_dir="${ROOT_DIR}/${PERIOD}"
    prune_backups "$period_dir"
  done
}


checkem
make_backups
prune_all
