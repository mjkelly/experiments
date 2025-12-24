#!/bin/bash
# Usage:
# 1. Invoke the script with no args to generate a directory file and set up the
#    container. We stop any existing container if it's running. (It's idempotent.)
# 2. Pass the arg "lazy" to just rebuild the directory file. The directory
#    container should pick this up immediately.
#
# This script lazily assumes you're in the docker-tmpl directory.
set -x
if [[ $1 = "lazy" ]]; then
  LAZY=1
else
  LAZY=0
fi

sudo ./venv/bin/python3 ./generate-cfg.py \
  --template ./templates/haproxy-directory.tmpl > $HOME/directory.html || exit

if [[ $LAZY -eq 1 ]]; then
  echo "lazy mode: skipping container restart"
  exit 0
fi

sudo docker rm -f dir
sudo docker run \
  --name dir \
  --mount type=bind,src=$HOME/directory.html,dst=/usr/share/nginx/html/index.html \
  -p 8082:80 \
  --restart unless-stopped \
  --label http-port=8082 \
  --label 'traefik.http.routers.dir.tls=true'  \
  --label 'traefik.http.services.dir.loadbalancer.server.port=80' \
  -d \
  nginx
