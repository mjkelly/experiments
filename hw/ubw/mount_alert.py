#!/usr/bin/python
# -----------------------------------------------------------------
# mount_alert.py -- Raise one pin if a filesystem is mounted at the given mount
# point, and another if it's not. The idea is to hook up LEDs or obnoxious
# buzzers to the pins.
#
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

# This is the mount point to check.
mountpoint = '/mnt/formenos'

# The pins to use for output
RED_LED = 'b0'
GREEN_LED = 'b1'

def drive_mounted():
  # Check if the drive is mounted by parsing /etc/mtab.
  fh = open('/etc/mtab')
  contents = fh.read()
  mounted = False
  for line in contents.split('\n'):
    line_parts = line.split(' ')
    logging.debug("line = %s" % line_parts)
    if len(line_parts) > 1 and line_parts[1] == mountpoint:
      logging.info("found %s in mtab" % mountpoint)
      mounted = True
      break
  fh.close()
  return mounted


logging.basicConfig(level=logging.INFO)
bw = bitwhacker.BitWhacker('/dev/ttyACM0')
logging.info("Sucessfully opened device")

bw.set_direction(RED_LED, True)
bw.set_direction(GREEN_LED, True)

bw.set_value(RED_LED, 0)
bw.set_value(GREEN_LED, 0)
time.sleep(0.2)
bw.set_value(RED_LED, 1)
bw.set_value(GREEN_LED, 1)
time.sleep(0.2)
bw.set_value(RED_LED, 0)
bw.set_value(GREEN_LED, 0)

# The mount flag is unset so we'll always write to the device on the first run.
mounted = None
while True:
  new_mounted = drive_mounted()

  logging.info("mount state: %s" % new_mounted)
  # We only write to the device on a state change.
  if new_mounted != mounted:
    if new_mounted:
      logging.info("activating green led")
      bw.set_value(GREEN_LED, 1)
      bw.set_value(RED_LED, 0)
    else:
      logging.info("activating red led")
      bw.set_value(RED_LED, 1)
      bw.set_value(GREEN_LED, 0)
  mounted = new_mounted

  time.sleep(1)

bw.close()
