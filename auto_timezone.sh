#!/bin/bash
# Uses free online services to automatically set your timezone. This is
# intended for a laptop that moves from place to place with you.
set -e
set -u

# An API key is free for 1000 requests per day. See:
# https://ipgeolocation.io/pricing.html
# Write .ipgeolocation.io in your home directory with the following format:
# IP_LOCATION_API_KEY=<API KEY>
. ~/.ipgeolocation.io

ip=$(curl --silent http://ipv4.icanhazip.com)
# We use the timezone API as documented here:
# https://ipgeolocation.io/documentation/timezone-api.html
timezone=$(curl --silent "https://api.ipgeolocation.io/timezone?apiKey=${IP_LOCATION_API_KEY}&ip=${ip}" | jq -r .timezone)

echo -n "Set timezone to ${timezone}? [y/N] "
read answer
answer=$(echo $answer | tr A-Z a-z)
if [[ $answer = "y" || $answer = "yes" ]]; then
  sudo timedatectl set-timezone $timezone
else
  echo "Aborted."
  exit 1
fi
