#!/usr/bin/env python
# vim: set sw=2 ts=2 expandtab:
#
# Reads the temperature from a TMP36 chip via SPI data from an MCP3008.
# Outputs data to a log, and keeps a running average of the last few recent
# temp readings.
#
# This script writes to 3 external files: See LOG_FILE, PID_FILE, and
# CURRENT_TEMP_FILE. The init-script uses PID_FILE, the munin plugin uses
# CURRENT_TEMP_FILE, and nothing external uses LOG_FILE.
#
# Based on adafruit-cosm-temp.py from:
# https://gist.github.com/ladyada/3249416#file-adafruit-cosm-temp-py
# Changes:
# - Removed COSM stuff
# - Output date+time
#
# Michael Kelly (michael@michaelkelly.org)
# Sat Feb 16 21:47:25 EST 2013

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
parser.add_option('--pidfile', dest='pidfile',
    default='/var/run/%s.pid' % bin_name,
    help='Where to write PID on startup, if --daemonize is true.')
parser.add_option('--logfile', dest='logfile',
    default='/var/log/%s.log' % bin_name,
    help='Where to write logs, if --daemonize is true.')
parser.add_option('--tempfile', dest='tempfile',
    default='/var/run/current_temp_c',
    help='Where to write current temperature.')
parser.add_option('--web', dest='web', action='store_true', default=False,
    help='Whether to set up read-only web interface for the data.')
parser.add_option('--listen', dest='listen', default='0.0.0.0:8080',
    help='What address and port to bind to if --web is true.')
parser.add_option('--testing', dest='testing', action='store_true', default=False,
    help='In testing mode, we fake the data from the temp sensor.')
opts, _ = parser.parse_args()

# Delay importing this module so we can test the rest of this script anywhere.
if not opts.testing:
  import RPi.GPIO as GPIO

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

SLEEP_TIME_S = 30


### Globals ###

logger = None
http_server = None
recent_temps = []

### Functions ###

def init_logging():
  # Initialize logging object first so functions can use it.
  if opts.daemonize:
    logging_handler = logging.handlers.RotatingFileHandler(
        filename=opts.logfile, maxBytes=100*1024*1024, backupCount=5)
  else:
    logging_handler = logging.StreamHandler(stream=sys.stderr)

  logging_handler.setLevel(logging.INFO)
  logging_handler.setFormatter(logging.Formatter(
      '%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s'))
  l = logging.getLogger('temp-logger')
  l.setLevel(logging.DEBUG)
  l.addHandler(logging_handler)
  return l

def init_gpio():
  if opts.testing:
    return

  GPIO.setmode(GPIO.BCM)
  # set up the SPI interface pins
  GPIO.setup(SPIMOSI, GPIO.OUT)
  GPIO.setup(SPIMISO, GPIO.IN)
  GPIO.setup(SPICLK, GPIO.OUT)
  GPIO.setup(SPICS, GPIO.OUT)

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
  """Reads SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)."""
  if ((adcnum > 7) or (adcnum < 0)):
    return -1

  if opts.testing:
    return 200

  GPIO.output(cspin, True)

  GPIO.output(clockpin, False)  # start clock low
  GPIO.output(cspin, False)     # bring CS low

  commandout = adcnum
  commandout |= 0x18  # start bit + single-ended bit
  commandout <<= 3    # we only need to send 5 bits here
  for i in range(5):
    if (commandout & 0x80):
      GPIO.output(mosipin, True)
    else:   
      GPIO.output(mosipin, False)
    commandout <<= 1
    GPIO.output(clockpin, True)
    GPIO.output(clockpin, False)

  adcout = 0
  # read in one empty bit, one null bit and 10 ADC bits
  for i in range(12):
    GPIO.output(clockpin, True)
    GPIO.output(clockpin, False)
    adcout <<= 1
    if (GPIO.input(misopin)):
      adcout |= 0x1

  GPIO.output(cspin, True)

  adcout /= 2       # first bit is 'null' so drop it
  return adcout

def output_data(data_read_time, read_adc0, millivolts, temp_C):
  # remove decimal point from millivolts
  millivolts = int(millivolts)

  # convert celsius to fahrenheit
  temp_F = (temp_C * 9.0 / 5.0) + 32

  logger.info("Read: time=%s, read_adc0=%s, mV=%s, "
               "temp_C=%.1f, temp_F=%.1f", data_read_time, read_adc0,
               millivolts, temp_C, temp_F)

  recent_temps.append(float(temp_C))
  while len(recent_temps) > 5:
    recent_temps.pop(0)
  logger.info("Last 5 temps (C): %s", recent_temps)

  recent_average = sum(recent_temps)/len(recent_temps)
  logger.info("Recent Average (C): %s", recent_average)
  try:
    with open(opts.tempfile, 'w') as fh:
      fh.write("%.1f\n" % recent_average)
  except Exception as e:
    logger.error("Error writing current temperature: %s", e)


def init_web(state):
  if not opts.web:
    return None

  class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def _format(self, s):
        return s.format(temp_c=state['temp_c'],
            last_read=state['last_read'])

    def _serve_metrics(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; version=0.0.4')
        self.end_headers()
        output = self._format('\n'.join([
          '# HELP temp_c Temperature (Celsius)',
          '# TYPE temp_c gauge',
          'temp_c {temp_c}',
          '',
          '# HELP last_read Time of last sensor read, in unix time',
          '# TYPE last_read gauge',
          'last_read {last_read}',
        ]))
        self.wfile.write(output + '\n')

    def _serve_text(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        output = self._format('\n'.join([
          'Temp (C): {temp_c}',
          'Last read time: {last_read}',
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

logger = init_logging()

if opts.daemonize:
  # Daemonize. (There are libraries to do this, but I'm trying to keep this as
  # self-contained as possible.)
  logger.info('parent getpid = %s' % os.getpid())

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
  logger.info('child getpid = %s' % os.getpid())

  with open(opts.pidfile, 'w') as fh:
    fh.write(str(os.getpid()))


state = {'temp_c': None, 'last_read': None}
init_gpio()
http_server = init_web(state)

logger.info('Starting.')

# temperature sensor connected channel 0 of mcp3008
adcnum = 0

### Main loop ###
try:
  while True:
    # read the analog pin (temperature sensor LM35)
    read_adc0 = readadc(adcnum, SPICLK, SPIMOSI, SPIMISO, SPICS)
    state['last_read'] = int(time.time())

    # convert analog reading to millivolts = ADC * (3300 / 1024)
    millivolts = read_adc0 * (3300.0 / 1024.0)

    # 10 mv per degree
    state['temp_c'] = ((millivolts - 100.0) / 10.0) - 40.0

    output_data(datetime.datetime.now(), read_adc0, millivolts, state['temp_c'])

    time.sleep(SLEEP_TIME_S)
except KeyboardInterrupt:
  logger.info('got keyboard interrupt -- stopping.')
  if http_server is not None:
    logger.info('http_server stopping...')
    http_server.shutdown()
    logger.info('http_server stopped')
  sys.exit(-1)

