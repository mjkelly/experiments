#!/bin/bash
# This is an example of how I run transmission. It is not intended to be universal.
cd $(dirname $0)
docker run -d \
  -p=127.0.0.1:9091:9091 \
  -v /data2/download/torrent:/torrent \
  -t mjkelly/transmission
