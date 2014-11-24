#!/bin/bash
# This is an example of how I run transmission. It is not intended to be universal.
cd $(dirname $0)
docker run -d \
  -p=127.0.0.1:9091:9091 \
  -p=49164:49164 \
  -v /data2/download/torrent:/torrent \
  -t mjkelly/transmission
