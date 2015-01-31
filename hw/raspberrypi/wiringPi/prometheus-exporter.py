#!/usr/bin/env python
# vim: set sw=2 ts=2 expandtab:
#
# Reads temperature value saved in a file and exports a Prometheus metrics
# page.
#
# Michael Kelly (michael@michaelkelly.org)
# Sat Jan 31 17:25:22 EST 2015

import BaseHTTPServer
import datetime
import logging
import logging.handlers
import optparse
import os
import os.path
import sys
import threading
import time

bin_name = os.path.basename(sys.argv[0])
parser = optparse.OptionParser()
parser.add_option('--no-daemonize', dest='daemonize', action='store_false', default=True,
    help='Whether to disconnect from terminal on startup. If this is false, we '
    'do not write to --pidfile or --logfile (we skip writing our PID, and logs '
    'go to stderr).')
parser.add_option('--tempfile', dest='tempfile',
    default='/var/tmp/current_temp_c',
    help='Where to write current temperature.')
parser.add_option('--listen', dest='listen', default='0.0.0.0:8080',
    help='What address and port to bind to if --web is true.')
opts, _ = parser.parse_args()

SLEEP_TIME_S = 15

### Globals ###

http_server = None

### Functions ###
def init_web(state):
  class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def _format(self, s):
        return s.format(temp_c=state['temp_c'],
            last_update=state['last_update'])

    def _serve_metrics(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; version=0.0.4')
        self.end_headers()
        output = self._format('\n'.join([
          '# HELP temp_c Temperature (Celsius)',
          '# TYPE temp_c gauge',
          'temp_c {temp_c}',
          '',
          '# HELP last_update Last update to temperature file, in unix time',
          '# TYPE last_update gauge',
          'last_update {last_update}',
        ]))
        self.wfile.write(output + '\n')

    def _serve_text(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        output = self._format('\n'.join([
          'Temp (C): {temp_c}',
          'Last update time: {last_update}',
        ]))
        self.wfile.write(output + '\n')

    def do_GET(self):
      if self.path == '/metrics':
        self._serve_metrics()
      else:
        self._serve_text()
  
  host, port = opts.listen.split(':', 2)
  port = int(port)
  http_server = BaseHTTPServer.HTTPServer((host, port), Handler)
  http_thread = threading.Thread(target=http_server.serve_forever)
  http_thread.start()
  return http_server

### End of functions ###

### Initialization ###
if opts.daemonize:
  # Daemonize. (There are libraries to do this, but I'm trying to keep this as
  # self-contained as possible.)
  pid = os.fork()
  if pid < 0:
    sys.exit(1)
  if pid > 0:
    sys.exit(0)  # parent exits

  # make our own process group
  os.setsid()

  # erase context from caller
  os.chdir('/')

  sys.stdout.flush()
  sys.stderr.flush()

  new_fd = os.open('/dev/null', os.O_RDWR)
  os.dup2(new_fd, sys.stdout.fileno())
  os.dup2(new_fd, sys.stderr.fileno())
  os.dup2(new_fd, sys.stdin.fileno())
  # done daemonizing
  with open(opts.pidfile, 'w') as fh:
    fh.write(str(os.getpid()))


state = {'temp_c': 0, 'last_update': 0}
http_server = init_web(state)

### Main loop ###
try:
  while True:
    mtime = os.stat(opts.tempfile).st_mtime
    if mtime > state['last_update']:
      state['last_update'] = mtime
      with open(opts.tempfile, 'r') as fh:
        state['temp_c'] = fh.readline().strip()
    time.sleep(SLEEP_TIME_S)
except KeyboardInterrupt:
  logger.info('got keyboard interrupt -- stopping.')
  if http_server is not None:
    logger.info('http_server stopping...')
    http_server.shutdown()
    logger.info('http_server stopped')
  sys.exit(-1)

