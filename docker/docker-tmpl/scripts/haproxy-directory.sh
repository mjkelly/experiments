#!/bin/bash
sudo ./docker-tmpl/venv/bin/python3 ./docker-tmpl/generate-cfg.py \
  --template docker-tmpl/templates/haproxy-directory.tmpl > $HOME/directory.html || exit
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
