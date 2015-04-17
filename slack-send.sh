#!/bin/bash
# This script sends a message to a slack server via slackbot remote control:
# https://api.slack.com/slackbot
# 
# The configuration file $HOME/slack-conf should define one variable, "URL",
# which is the webhook URL for your slackbot.

# Abort on unused variables, and failed commands.
set -u
set -e

. $HOME/slack-conf
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <channel> <message>" >&2
  echo "'channel' does not start with the '#'." >&2
  exit 2
fi
channel="$1"
msg="$2"

output=$(curl --silent --data "${msg}" "${URL}&channel=%23${channel}" | sed 's/ok//')
if [ ! -z "${output}" ]; then
  echo "${output}"
  exit 1
fi
