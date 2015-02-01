#!/usr/bin/env python
# vim: set sw=2 ts=2 expandtab:
#
# Reads temperature value saved in a file and exports a Prometheus metrics
# page. This is a companion to read-temp.c in this directory, which populates
# the temperature file.
#
# Because this script doesn't daemonize and doesn't keep a pidfile, etc, the
# best way to trigger it is with an @reboot line in a crontab:
#
# @reboot prometheus-exporter.py >/dev/null 2>&1 &
#
# Michael Kelly (michael@michaelkelly.org)
# Sat Jan 31 17:25:22 EST 2015

import BaseHTTPServer
import optparse
import os
import os.path
import sys
import threading
import time

bin_name = os.path.basename(sys.argv[0])
parser = optparse.OptionParser()
parser.add_option('--tempfile', dest='tempfile',
    default='/var/run/current_temp_c',
    help='Where to write current temperature.')
parser.add_option('--listen', dest='listen', default='0.0.0.0:8080',
    help='What address and port to bind.')
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
  if http_server is not None:
    http_server.shutdown()
  sys.exit(-1)

