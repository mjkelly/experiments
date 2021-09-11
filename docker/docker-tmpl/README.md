# docker-tmpl

This is a very simple but general tool to generate output files based on the
local host's running docker containers.

This is useful if you want to generate a configuration for a reverse proxy, or
a status page showing running containers.

We take Jinja2 templates as input, which can be quite complex.

## Setup

Using docker-tmpl requires python3.

To set up, `make`. This will install the packages you need into a virtualenv. 

## Running

From the docker-tmpl directory, type:
```
./venv/bin/python3 ./generate-cfg.py --help
```

Here are some example invocations:

Generate an HTML directory of running containers:
```
./venv/bin/python3 ./generate-cfg.py \
  --template docker-html.tmpl \
  > $HOME/directory.html
```

Generate an haproxy.cfg based on running containers, overriding virtualhost
hostnames and providing a TLS private key:
```
./venv/bin/python3 ./generate-cfg.py \
  --hostname foo.example.com \
  --var tls_cert=/ssl/fullchain-privkey.pem \
  --template docker-haproxy.html \
  > $HOME/haproxy.cfg
```

## Example templates

There are two example templates, which can work nicely together. There's a lot
of duplicated logic up at the top of the two examples, since we force
basically all logic into the templates themselves.

### docker-haproxy.tmpl

This is a working example that generates an haproxy config for a reverse proxy
that fronts docker containers using virtual hosts based on container name. It's
an example of how much logic you can put into your template.

It supports exposing one port per docker container, specified with the
`http_port` or `tls_port` docker label.

It supports TLS on the frontend if you give it a private key.

Here's an example that ties all of this together:
```
#!/bin/bash
sudo ./docker-tmpl/venv/bin/python3 ./docker-tmpl/generate-cfg.py \
  --hostname foo.docker.example.com \
  --template docker-tmpl/docker-haproxy.tmpl > $HOME/haproxy.cfg || exit
sudo docker rm -f haproxy
sudo docker run \
  --name haproxy \
  --restart unless-stopped \
  --label role=frontend \
  --mount type=bind,src=$HOME/haproxy.cfg,dst=/etc/haproxy.cfg \
  --mount type=bind,src=$HOME/ssl/docker.example.name/fullchain-privkey.pem,dst=/ssl/fullchain-privkey.pem \
  -p 8090:8090 \
  -p 80:80 \
  -p 443:443 \
  -d \
  haproxy \
  haproxy -f /etc/haproxy.cfg
```

We run `docker rm` first so we can re-run this script to update the page. (Very
crude, yes, but it keeps everything contained to one command.)

### docker-html.tmpl

This shows a very simple directory of docker services. We try to link to
exposed services as well, as they would be exposed via docker-haproxy.tmpl.

Here's an example that uses this template and exposes it via an nginx image:
```
#!/bin/bash
sudo ./docker-tmpl/venv/bin/python3 ./docker-tmpl/generate-cfg.py \
  --hostname foo.docker.example.name \
  --var tls_cert=/ssl/fullchain-privkey.pem \
  --template docker-tmpl/docker-html.tmpl > $HOME/directory.html || exit
sudo docker rm -f dir
sudo docker run \
  --name dir \
  --mount type=bind,src=$HOME/directory.html,dst=/usr/share/nginx/html/index.html \
  --label http-port=8100 \
  -p 8100:80 \
  --restart unless-stopped \
  -d \
  nginx
```

