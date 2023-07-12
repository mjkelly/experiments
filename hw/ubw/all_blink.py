#!/usr/bin/python
# -----------------------------------------------------------------
# blink_all.py -- Blink all the pins with a loop.
#
# Copyright 2010 Michael Kelly (michael@michaelkelly.org)
#
# Sat Jan 29 18:50:58 EST 2011
# -----------------------------------------------------------------

import logging
import time

import bitwhacker

# The pins to use for output
pins = ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7',
        'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7']

logging.basicConfig(level=logging.INFO)
bw = bitwhacker.BitWhacker('/dev/ttyACM0')
logging.info("Sucessfully opened device")

for p in pins:
  bw.set_direction(p, True)

while True:
  logging.info('all on...')
  for p in pins:
    bw.set_value(p, 1)
  time.sleep(0.2)
  logging.info('all off...')
  for p in pins:
    bw.set_value(p, 0)
  time.sleep(0.2)

bw.close()
