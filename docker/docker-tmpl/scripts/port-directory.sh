#!/bin/bash
sudo ./docker-tmpl/venv/bin/python3 ./docker-tmpl/generate-cfg.py \
  --template docker-tmpl/templates/port-directory.tmpl > $HOME/directory.html || exit
sudo docker rm -f dir
sudo docker run \
  --name dir \
  --mount type=bind,src=$HOME/directory.html,dst=/usr/share/nginx/html/index.html \
  --label http-port=80 \
  --label link-container-name=true \
  --label 'traefik.http.routers.dir.tls=true'  \
  --label 'traefik.http.services.dir.loadbalancer.server.port=80' \
  -p 80:80 \
  --restart unless-stopped \
  -d \
  nginx
