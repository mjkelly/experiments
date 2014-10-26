#!/bin/bash
# This is an example of how I run apache. It is not intended to be universal.
cd $(dirname $0)
docker run -d \
  -p 8080:80 \
  -v /home/mkelly/attachments:/srv \
  -t mjkelly/apache
