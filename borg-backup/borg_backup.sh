#!/bin/bash
# Borg backup script based on:
#    https://borgbackup.readthedocs.io/en/stable/quickstart.html
# 
# Helper script to keep a set number of daily, weekly, and monthly backups.
#
# This won't initialize a repository that doesn't exist, so to do that, run
# something like this:
#    . $HOME/borg_backup_vars
#    borg init

# We use this to set BORG_REPO and BORG_PASSPHRASE or BORG_PASSCOMMAND. And any
# other env vars you need, like BORG_REMOTE_PATH.
. /root/borg_backup_vars

# some helpers and error handling:
info() { printf "\n%s %s\n\n" "$( date )" "$*" >&2; }
trap 'echo $( date ) Backup interrupted >&2; exit 2' INT TERM

info "Starting backup"

# Backup the most important directories into an archive named after
# the machine this script is currently running on:

borg create                         \
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
    /lib/systemd                    \
    /home                           \

# The original version of this script also saves:
#    /root
#    /var

backup_exit=$?

info "Pruning repository"

# Use the `prune` subcommand to a certain number of backups of THIS machine.
# The '{hostname}-*' glob is very important to limit prune's operation to this
# machine's archives and not apply to other machines' archives also:

borg prune                          \
    --list                          \
    --glob-archives '{hostname}-*'  \
    --show-rc                       \
    --keep-within   1d              \
    --keep-daily    14              \
    --keep-weekly   8               \
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
