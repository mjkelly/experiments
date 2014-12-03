#!/bin/bash
# This is an example of how I run transmission. It is not intended to be universal.
data="/data2/download/torrent"
config="$PWD/transmission-daemon-config"

cd $(dirname $0)
docker run -d \
  --restart=always \
  -p=127.0.0.1:9091:9091 \
  -p=49164:49164 \
  -v "${data}:/transmission/data" \
  -v "${config}:/transmission/config" \
  -t mjkelly/transmission
