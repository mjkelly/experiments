#!/bin/bash
sudo ./venv/bin/python3 ./generate-cfg.py \
  --template ./templates/port-directory.tmpl > $HOME/directory.html || exit
sudo docker rm -f dir
sudo docker run \
  --name dir \
  --mount type=bind,src=$HOME/directory.html,dst=/usr/share/nginx/html/index.html \
  -p 8082:80 \
  --restart unless-stopped \
  --label http-port=8082 \
  --label link-container-name=true \
  --label 'traefik.http.routers.dir.tls=true'  \
  --label 'traefik.http.services.dir.loadbalancer.server.port=80' \
  -d \
  nginx
