#!/bin/bash
# This is a simple script to help manage non-public bits of data
# that often accompany public source code.
# It's not a password manager, and you shouldn't use it to store passwords
# humans will use. It's a convenience for storing non-public data.
#
# First-time setup:
# - Create a non-public S3 bucket.
# - Set up the `aws` CLI. We use `aws s3` subcommands.
# - Write a file in ~/.credconfig that looks like this:
#     export CREDS_S3_BUCKET=<your s3 bucket>
#   You can optionally add another line:
#     export AWS_PROFILE=<name of aws profile to use>
PATH_FILE=.credpath
GLOBAL_CONFIG=$HOME/.credconfig

set -e
op=$1

function get_path() {
  echo "${CREDS_S3_BUCKET}/$(cat $PATH_FILE)"
}

if [[ ! -f "$GLOBAL_CONFIG" ]]; then
  echo "Global config $GLOBAL_CONFIG does not exist." >&2
  echo "See setup instructions at top of $0." >&2
  exit 3
fi
. $GLOBAL_CONFIG

if [[ -z $CREDS_S3_BUCKET ]]; then
  echo "\$CREDS_S3_BUCKET is not set." >&2
  echo "See setup instructions at top of $0." >&2
  exit 3
fi

if [[ ! -f "$PATH_FILE" ]]; then
  echo "Could not get credential path." >&2
  echo "Does $PATH_FILE exist in current directory?" >&2
  exit 3
fi

path=$(get_path)

if [[ $op == "push" ]]; then
  shift
  for f in "$@"; do
    aws --profile=$PROFILE s3 cp $f ${path}/$f
  done
elif [[ $op == "pull" ]]; then
  aws --profile=$PROFILE s3 sync ${path}/$f .
elif [[ $op == "ls" ]]; then
  aws --profile=$PROFILE s3 ls ${path}/$f
else
  echo "Unknown operation: ${op}" >&2
  echo "Valid operations are: push pull ls" >&2
  exit 2
fi
