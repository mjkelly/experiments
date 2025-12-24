#!/usr/bin/python3

import datetime
import socket

import docker
import jinja2
from absl import app
from absl import flags
from absl import logging

FLAGS = flags.FLAGS

flags.DEFINE_string('template', None, 'Jinja2 template to use as input.')
flags.DEFINE_multi_string('var', [],
                          'Extra template variables to pass to Jinja2.')
flags.mark_flag_as_required('template')


def main(argv):
    del argv  # Unused.
    hostname_full = socket.getfqdn()
    hostname = hostname_full.split('.')[0]
    domain = '.'.join(hostname_full.split('.')[1:])
    logging.info('Loading template %s', FLAGS.template)

    d = docker.from_env()
    containers = sorted(d.containers.list(), key=lambda c: c.name)

    vars = {
        'hostname': hostname,
        'hostname_full': hostname_full,
        'domain': domain,
        'now': datetime.datetime.now(),
        'containers': containers
    }

    extra_vars = {}
    for v in FLAGS.var:
        key, value = v.split("=", 1)
        extra_vars[key] = value

    logging.debug(f"Internal vars: {vars}")
    logging.debug(f"Extra vars (from command-line): {extra_vars}")

    vars.update(extra_vars)

    with open(FLAGS.template, 'r') as fh:
        template = jinja2.Template(fh.read())
    print(template.render(**vars))


if __name__ == '__main__':
    app.run(main)
