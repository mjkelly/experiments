# docker-tmpl

*Or, how I learned to stop worrying and replaced Traefik with 100 lines of Python!*

This is a very simple but general tool to generate output files based on the
local host's running docker containers.

This is useful if you want to generate a configuration for a reverse proxy, or
a status page showing running containers.

We take Jinja2 templates as input, which can be quite complex. This is where a
lot of the magic is.

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

Generate an haproxy.cfg based on running containers, overriding virtualhost
hostnames and providing a TLS private key:
```
./venv/bin/python3 ./generate-cfg.py \
  --var tls_cert=/ssl/fullchain-privkey.pem \
  --template templates/docker-haproxy.html \
  > $HOME/haproxy.cfg
```

If you're running a haproxy instance like the one above, and you have your
hostnames set up (so e.g. container.example.com points to `container`), you can
generate a directory by hostname:
```
./venv/bin/python3 ./generate-cfg.py \
  --template templates/haproxy-directory.tmpl \
  > $HOME/directory.html
```

If you're trying to debug why a template isn't working, pass `-v=1` to
`generate-cfg.py` and it'll output more verbose debug information.

## Scripts

There are idempotent scripts that start/update a container like this in
the `scripts/` directory. (NOTE: These scripts grab Docker state from just
before they start, so the directory container will not pick up _itself_ on its
first run. You can just re-run it to resolve this. This is true for all the
examples.)


## Using `port-directory.tmpl`

This template directs to hostports on a docker host. This is the simplest to
use. It just requires that you have your docker services exposed to your local
network.

### Docker Tags
You can configure the output of the port-directory script with the following
tags:
* `http-port`: The HTTP port exposed by container. We generate an `http://`
  link if we see this tag. (Mutually exclusive with `tls-port`.)
* `tls-port`: The TLS port exposed by the container. We generate an `https://`
  link if we see this tag. (Mutually exclusive with `http-port`.)
* `link-container-name`: If this has any non-empty value, we generate links
  based on the name of each container: `<container-name>.<domain>:<port>`.
    * `<domain>` comes from the domain of the container host, or the `domain`
      var.
    * `<port>` comes from the value of `http-port` or `tls-port`.

This template does not generate a link to a container one of `http-port` or
`tls-port` is not present. (We don't know if exposed ports are http/https UIs.)

## Using `haproxy-directory.tmpl`

This template directs to hostnames. This has more requirements:
* You must have a load balancer (such as the one from `haproxy.tmpl`) that will
  redirect requests to each host to its appropriate container. We don't rely on
  nonstandard port numbers anymore.
* You must have a DNS setup that will send traffic from different hostnames to
  your load balancer. The easiest way to do this is to use a wildcard, so
  `*.example.com` all goes to your load balancer.

### Docker tags
We will list any container that has either `http-port` or `tls-port`. We don't
actually use the value of the port here, because we assume directing to the
hostname is enough. (If it isn't, use `port-directory.tmpl`).

### Vars
You can pass `--var extra_links` to add more links here. This is a
comma-separated list of key=value pairs. The key is the name, the value is the
full link (including http/https scheme).

Example: `--var extra_links=Example=http://example.com`

## Using `haproxy.tmpl`

This generates a haproxy config for a load balancer that can be used to serve
requests from `haproxy-directory.tmpl`. This server should listen on ports 80
and 443 and DNS should point all container hostnames to it (for example via a
wildcard).

### Docker tags
* `http-port`: The HTTP port exposed by container. We health check this port.
  (Mutually exclusive with `tls-port`.)
* `tls-port`: The TLS port exposed by the container. We health check this port,
  but do not verify the cert. (Mutually exclusive with `http-port`.)

### Vars
You can pass `--var extra_http_backends` or `--var extra_tls_backends` to add
more custom backends. The format is a comma-separated list of key=value pairs.
The key is the local hostname (without domain) to use, and the value is the
backend host:port.

Example: `--var extra_tls_backends=fw=192.168.1.1:443`

If you also run `haproxy-directory.tmpl`, you may want to add these with `--var
extra_links`.

If you need more customization over backends, you should edit the template directly.
