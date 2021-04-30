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
./venv/bin/python3 ./generate-cfg --help
```

Here are some example invocations:

Generate an HTML report of running containers:
```
./venv/bin/python3 ./generate-cfg \
  --template docker-html.tmpl \
  > $HOME/docker-report.html
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

### docker-haproxy.tmpl

This is a working example that generates an haproxy config for a reverse proxy
that fronts docker containers using virtual hosts based on container name. It's
an example of how much logic you can put into your template.

It supports exposing one port per docker container, specified with the
`http_port` or `tls_port` docker label.

It supports TLS on the frontend if you give it a private key.

### docker-html.tmpl

This is a toy example that lists running container names and IDs in a table.
