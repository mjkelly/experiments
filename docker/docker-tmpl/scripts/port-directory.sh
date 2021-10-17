#!/bin/bash
sudo ./docker-tmpl/venv/bin/python3 ./docker-tmpl/generate-cfg.py \
  --var domain=example.com \
  --template docker-tmpl/templates/port-directory.tmpl > $HOME/directory.html || exit
sudo docker rm -f dir
sudo docker run \
  --name dir \
  --mount type=bind,src=$HOME/directory.html,dst=/usr/share/nginx/html/index.html \
  --label http-port=8100 \
  --label 'traefik.http.routers.dir.tls=true'  \
  --label 'traefik.http.services.dir.loadbalancer.server.port=80' \
  -p 8100:80 \
  --restart unless-stopped \
  --network monitoring \
  -d \
  nginx
