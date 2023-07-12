#!/usr/bin/python
# -----------------------------------------------------------------
# zmqchat.py -- $desc$
# Copyright 2010 Michael Kelly (michael@michaelkelly.org)
#
# Fri Feb 10 22:28:09 EST 2012
# -----------------------------------------------------------------

import zmq
import datetime
import sys
import threading

now = datetime.datetime.now

req_addr = 'tcp://127.0.0.1:5000'
pub_addr = 'tcp://127.0.0.1:5001'

context = zmq.Context()

publisher = context.socket(zmq.PUB)
publisher.bind(pub_addr)
print 'Bound to publish socket.'

req = context.socket(zmq.PULL)
req.bind(req_addr)
print 'Bound to reply socket.'

while True:
  message = req.recv()
  print "%s: got %s" % (now(), message)
  publisher.send(message)
