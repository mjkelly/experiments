#!/usr/bin/python3

import datetime
import os
import socket
import sys

import docker
import jinja2
from absl import app
from absl import flags
from absl import logging

HOSTNAME = socket.gethostname()

FLAGS = flags.FLAGS

flags.DEFINE_string('template', None, 'Jinja2 template to use as input.')
flags.DEFINE_string('hostname', HOSTNAME, 'Name of this host, used to determine names of backends')
flags.DEFINE_string('backend_host', HOSTNAME, 'Hostname to use as backend; this is how haproxy will reach the docker containers')
flags.DEFINE_multi_string('var', [], 'Extra template variables to pass to Jinja2.')
flags.mark_flag_as_required('template')

def main(argv):
	del argv  # Unused.
	hostname_full = FLAGS.hostname
	hostname = hostname_full.split('.')[0]
	domain = '.'.join(hostname_full.split('.')[1:])
	logging.info('Loading template %s', FLAGS.template)

	d = docker.from_env()
	containers = d.containers.list()

	extra_vars = {}
	for v in FLAGS.var:
		key, value = v.split("=", 1)
		extra_vars[key] = value

	with open(FLAGS.template, 'r') as fh:
		template = jinja2.Template(fh.read())
	print(template.render(
		**extra_vars,
		hostname=hostname,
		domain=domain,
		backend_host=FLAGS.backend_host,
		hostname_full=hostname_full,
		now=datetime.datetime.now(),
		containers=containers))


if __name__ == '__main__':
  app.run(main)
