#!/bin/bash
sudo ./docker-tmpl/venv/bin/python3 ./docker-tmpl/generate-cfg.py \
  --var domain=example.com \
  --template docker-tmpl/templates/haproxy.tmpl > $HOME/haproxy.cfg || exit
sudo docker rm -f haproxy
sudo docker run \
  --name haproxy \
  --restart unless-stopped \
  --label role=frontend \
  --mount type=bind,src=$HOME/haproxy.cfg,dst=/etc/haproxy.cfg \
  --mount type=bind,src=$HOME/ssl/d.quux.name/fullchain-privkey.pem,dst=/ssl/fullchain-privkey.pem \
  -p 8090:8090 \
  -p 80:80 \
  -p 443:443 \
  --network monitoring \
  -d \
  haproxy \
  haproxy -f /etc/haproxy.cfg
