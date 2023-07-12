#!/usr/bin/python
# -----------------------------------------------------------------
# bitwhacker.py -- A simple library for interacting with a USB Bit Whacker
# (with default firmware) over the serial interface.
# 
# Tested with the 1.4.3 firmware.
#
# Copyright 2010 Michael Kelly (michael@michaelkelly.org)
#
# Sat Jan 29 21:38:46 EST 2011
# -----------------------------------------------------------------

import logging

class PinNameError(Exception):
  """A pin name was mis-specified."""
  pass

class BitWhacker(object):
  """A USB Bit Whacker.
  
  Naming conventions:
    pins: Pins are named A0 through A7 and B0 through B7. You can address them
    as 2-letter strings, with upper or lowercase letters.
  """
  # TODO:
  # - Support more commands!
  # - Keep track of pin input/output status and raise errors if you try to
  #   output to an input pin, etc.

  def __init__(self, path):
    """Creates a new BitWhacker whose serial interface is on the given path.
    
    path = "/dev/ttyACM0" is typical.
    """
    self._path = path
    self._fh = open(path, 'w')

  def set_pin(self, led, state):
    self._fh.write('po,%s,%s\r' % (led, state))
    self._fh.flush()

  def _pin(self, pin):
    # The docs say something about [ABC][0-7] being valid, but I don't see any
    # C pins on my UBW.
    if len(pin) != 2:
      raise PinNameError('Bad length')
    pin = pin.lower()
    name, number = pin[0], pin[1]
    if name not in set(['a', 'b']):
      raise PinNameError("Pin name must start with 'A' or 'B'.")
    if int(number) > 7:
      raise PinNameError('Pin number must be in range 0-7.')
    return '%s,%s' % (name, number)

  def set_direction(self, pin, output):
    """Set a pin's direction (input or output).
    
    Args:
      pin: (str) a pin number
      output: (bool) If the pin should be an output pin. Otherwise it is input.
    """
    if output:
      self._write('pd,%s,0\r' % self._pin(pin))
    else:
      self._write('pd,%s,1\r' % self._pin(pin))

  def set_value(self, pin, value):
    """Set an output pin's value. The pin must already be set as an output pin.

    Args:
      pin: (str) a pin number
      value: (int) integer value for the pin
    """
    if value < 0 or value > 255:
      raise RuntimeError('Value %d for pin %s out of range (must be [0-255]).'
          % (value, pin))
    self._write('po,%s,%d' % (self._pin(pin), value))

  def _write(self, s):
    """Writes to the device, handling line endings and flushing."""
    logging.debug('UBW writing: %s' % s)
    self._fh.write(s + '\r')
    self._fh.flush()

  def close(self):
    """Shut down any connection to the USB Bit Whacker."""
    self._fh.close()

