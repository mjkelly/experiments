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

import logging
import time

import bitwhacker

logging.basicConfig(level=logging.DEBUG)

bw = bitwhacker.BitWhacker('/dev/ttyACM0')
logging.info("Sucessfully opened device")

RED_LED = 'b0'

bw.set_direction(RED_LED, True)

sleep_max = 0.5
sleep_min = 0.005
sleep_secs = sleep_max
sleep_mult = 0.8
while True:
  logging.info("sleep_secs = %f", sleep_secs)
  logging.info("turning on")
  bw.set_value(RED_LED, 1)
  time.sleep(sleep_secs)

  logging.info("turning off")
  bw.set_value(RED_LED, 0)
  time.sleep(sleep_secs)

  if sleep_secs <= sleep_min:
    logging.info("switching to INCREASED time")
    sleep_mult = 1.25
  if sleep_secs >= sleep_max:
    sleep_mult = 0.8
    logging.info("switching to DECREASED time")
  sleep_secs *= sleep_mult

bw.close()
