# docker-tmpl

This is a very simple but general tool to generate output files based on the
local host's running docker containers.

This is useful if you want to generate a configuration for a reverse proxy, or
a status page showing running containers.

We take Jinja2 templates as input, which can be quite complex.

## Setup

Using docker-tmpl requires python3, and a working docker setup.

To set up, `make`. This will install the packages you need into a virtualenv. 

## Running

From the docker-tmpl directory, type:
```
./venv/bin/python3 ./generate-cfg.py --help
```

## Examples

Here are some example invocations:

Generate an HTML directory of running containers:
```
./venv/bin/python3 ./generate-cfg.py \
  --template templates/port-directory.tmpl \
  > $HOME/directory.html
```
There is an idempotent script that starts/updates a container like this in
`scripts/port-directory.sh`.

Generate an haproxy.cfg based on running containers, overriding virtualhost
hostnames and providing a TLS private key:
```
./venv/bin/python3 ./generate-cfg.py \
  --var domain=example.com \
  --var tls_cert=/ssl/fullchain-privkey.pem \
  --template docker-haproxy.html \
  > $HOME/haproxy.cfg
```
There is an idempotent script that starts/updates a container like this in
`scripts/haproxy.sh`.


If you're running a haproxy instance like the one above, and you have your
hostnames set up (so e.g. container.example.com points to `container`), you can
generate a directory by hostname:
```
./venv/bin/python3 ./generate-cfg.py \
  --template templates/haproxy-directory.tmpl \
  > $HOME/directory.html
```
There is an idempotent script that starts/updates a container like this in
`scripts/haproxy-directory.sh`.

If you're trying to debug why a template isn't working, pass `-v=1` to
`generate-cfg.py` and it'll output more verbose debug information.
