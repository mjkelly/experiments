#!/usr/bin/python
# -----------------------------------------------------------------
# bitwhack.py -- $desc$
# Copyright 2010 Michael Kelly (michael@michaelkelly.org)
#
# This program is released under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Sat Jan 29 18:50:58 EST 2011
# -----------------------------------------------------------------

import sys
import os
import logging
import time

mountpoint = '/mnt/formenos'

class BitWhacker(object):
  """A class to speed up interaction with the bitwhacker.

  This is not a general class for interacting with the bitwhacker -- it's
  provides only abstractions that are useful to this program.
  """
  RED_LED = 'b,0'
  GREEN_LED = 'b,1'
  LED_ON = '1'
  LED_OFF = '0'

  def __init__(self, path):
    self._path = path
    self._fh = open(path, 'w')

  def set_led(self, led, state):
    self._fh.write('po,%s,%s\r' % (led, state))
    self._fh.flush()

  def setup(self):
    self._fh.write('pd,b,0,0\r')
    self._fh.write('pd,b,1,0\r')
    self._fh.flush()

  def close(self):
    self._fh.close()


logging.basicConfig(level=logging.INFO)
bw = BitWhacker('/dev/ttyACM0')
logging.info("Sucessfully opened device")
bw.setup()

bw.set_led(BitWhacker.RED_LED, BitWhacker.LED_OFF)
bw.set_led(BitWhacker.GREEN_LED, BitWhacker.LED_OFF)
time.sleep(0.2)
bw.set_led(BitWhacker.RED_LED, BitWhacker.LED_ON)
bw.set_led(BitWhacker.GREEN_LED, BitWhacker.LED_ON)
time.sleep(0.2)
bw.set_led(BitWhacker.RED_LED, BitWhacker.LED_OFF)
bw.set_led(BitWhacker.GREEN_LED, BitWhacker.LED_OFF)

# The mount flag is unset so we'll always write to the device on the first run.
mounted = None
while True:
  fh = open('/etc/mtab')
  contents = fh.read()
  new_mounted = False
  for line in contents.split('\n'):
    line_parts = line.split(' ')
    logging.debug("line = %s" % line_parts)
    if len(line_parts) > 1 and line_parts[1] == mountpoint:
      logging.info("found %s in mtab" % mountpoint)
      new_mounted = True
      break
  fh.close()

  logging.info("mount state: %s" % new_mounted)
  # We only write to the device on a state change.
  if new_mounted != mounted:
    if new_mounted:
      logging.info("activating green led")
      bw.set_led(BitWhacker.GREEN_LED, BitWhacker.LED_ON)
      bw.set_led(BitWhacker.RED_LED, BitWhacker.LED_OFF)
    else:
      logging.info("activating red led")
      bw.set_led(BitWhacker.RED_LED, BitWhacker.LED_ON)
      bw.set_led(BitWhacker.GREEN_LED, BitWhacker.LED_OFF)
  mounted = new_mounted

  time.sleep(1)

bw.close()
