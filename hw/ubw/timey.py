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

logging.basicConfig(level=logging.INFO)

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


bw = BitWhacker('/dev/ttyACM0')
logging.info("Sucessfully opened device")
bw.setup()

sleep_max = 0.5
sleep_min = 0.005
sleep_secs = sleep_max
sleep_mult = 0.8
while True:
  logging.info("sleep_secs = %f", sleep_secs)
  logging.info("turning on")
  bw.set_led(BitWhacker.RED_LED, BitWhacker.LED_ON)
  time.sleep(sleep_secs)

  logging.info("turning off")
  bw.set_led(BitWhacker.RED_LED, BitWhacker.LED_OFF)
  time.sleep(sleep_secs)

  if sleep_secs <= sleep_min:
    logging.info("switching to INCREASED time")
    sleep_mult = 1.25
  if sleep_secs >= sleep_max:
    sleep_mult = 0.8
    logging.info("switching to DECREASED time")
  sleep_secs *= sleep_mult

bw.close()
