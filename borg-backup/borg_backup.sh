#!/bin/bash
# Borg backup script based on:
#    https://borgbackup.readthedocs.io/en/stable/quickstart.html
# 
# Helper script to keep a set number of daily, weekly, and monthly backups.
#
# This won't initialize a repository that doesn't exist, so to do that, run
# something like this:
#    . $HOME/borg_backup_vars
#    borg init $EXTRA_BORG_ARGS

# We use this to set EXTRA_BORG_ARGS, BORG_REPO and BORG_PASSPHRASE or
# BORG_PASSCOMMAND.
. $HOME/borg_backup_vars

# some helpers and error handling:
info() { printf "\n%s %s\n\n" "$( date )" "$*" >&2; }
trap 'echo $( date ) Backup interrupted >&2; exit 2' INT TERM

info "Starting backup"

# Backup the most important directories into an archive named after
# the machine this script is currently running on:

borg create                         \
    $EXTRA_BORG_ARGS                \
    --verbose                       \
    --filter AME                    \
    --list                          \
    --stats                         \
    --show-rc                       \
    --compression lz4               \
    --exclude-caches                \
    --exclude '/home/*/.cache/*'    \
    --exclude '/home/*/Downloads/*' \
    --exclude '/var/cache/*'        \
    --exclude '/var/tmp/*'          \
    '::{hostname}-{now}'            \
    /etc                            \
    /home                           \

# The original version of this script also saves:
#    /root
#    /var

exit 10

backup_exit=$?

info "Pruning repository"

# Use the `prune` subcommand to maintain 7 daily, 4 weekly and 6 monthly
# archives of THIS machine. The '{hostname}-' prefix is very important to
# limit prune's operation to this machine's archives and not apply to
# other machines' archives also:

borg prune                          \
    $EXTRA_BORG_ARGS                \
    --list                          \
    --prefix '{hostname}-'          \
    --show-rc                       \
    --keep-within   1d              \
    --keep-daily    7               \
    --keep-weekly   4               \
    --keep-monthly  6               \

prune_exit=$?

# use highest exit code as global exit code
global_exit=$(( backup_exit > prune_exit ? backup_exit : prune_exit ))

if [ ${global_exit} -eq 1 ];
then
    info "Backup and/or Prune finished with a warning"
fi

if [ ${global_exit} -gt 1 ];
then
    info "Backup and/or Prune finished with an error"
fi

exit ${global_exit}
