#!/bin/bash
# Usage:
# 1. Invoke the script with no args to generate a config file and set up the
#    container. We stop any existing container if it's running. (It's idempotent.)
# 2. Pass the arg "lazy" to just rebuild the config and send SIGHUP to the
#    haproxy container to reload the config.
#
# This script lazily assumes you're in the docker-tmpl directory.
set -x
if [[ $1 = "lazy" ]]; then
  LAZY=1
else
  LAZY=0
fi

# Prep certs - this is designed to work with what letsencrypt provides you.
# ($CERTS_DIR should be a link to an individual directory in the live/
# directory.)
CERT_DIR="$HOME/haproxy-ssl"
COMBINED="$CERT_DIR/fullchain-privkey.pem"
HAIN="$CERT_DIR/fullchain.pem"
PRIVKEY="$CERT_DIR/privkey.pem"
if [[ $CHAIN -nt $COMBINED || $PRIVKEY -nt $COMBINED ]]; then
  cat $CHAIN $PRIVKEY > $COMBINED
fi
# Generate config
sudo ./venv/bin/python3 ./generate-cfg.py \
  --var tls_cert=/ssl/fullchain-privkey.pem \
  --template ./templates/haproxy.tmpl > $HOME/haproxy.cfg || exit

if [[ $LAZY -eq 1 ]]; then
  echo "lazy mode: reloading haproxy"
  sudo docker kill -s HUP haproxy
  exit 0
fi

sudo docker rm -f haproxy
# 8090 is the admin port
# 80 and 443 are serving ports
# All are referenced in the haproxy config.
sudo docker run \
  --name haproxy \
  --restart unless-stopped \
  --label http-port=8090 \
  --label role=frontend \
  --mount type=bind,src=$HOME/haproxy.cfg,dst=/etc/haproxy.cfg \
  --mount type=bind,src=$COMBINED,dst=/ssl/fullchain-privkey.pem \
  -p 8090:8090 \
  -p 80:80 \
  -p 443:443 \
  -d \
  haproxy \
  haproxy -f /etc/haproxy.cfg
sleep 1
sudo docker logs haproxy
