#!/usr/bin/python
# -----------------------------------------------------------------
# zmqchat.py -- $desc$
# Copyright 2010 Michael Kelly (michael@michaelkelly.org)
#
# This program is released under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Fri Feb 10 22:28:09 EST 2012
# -----------------------------------------------------------------

import zmq
import datetime
import sys
import threading

now = datetime.datetime.now
myname = sys.argv[1]

req_addr = 'tcp://127.0.0.1:5000'
pub_addr = 'tcp://127.0.0.1:5001'

class RecvThread(threading.Thread):
  def run(self):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(pub_addr)
    subscriber.setsockopt(zmq.SUBSCRIBE, 'msg:')
    print 'Bound to subscription socket.'

    while True:
      message = subscriber.recv()
      print '\n%s: %s' % (now(), message)


context = zmq.Context()

sender = context.socket(zmq.PUSH)
sender.connect(req_addr)
print 'Connected to request socket as %s.' % myname

receiver = RecvThread()
receiver.start()

while True:
  message = '%s: %s' % (myname, sys.stdin.readline().strip())
  sender.send('msg:%s' % message)

