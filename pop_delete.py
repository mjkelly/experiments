#!/usr/bin/python
# -----------------------------------------------------------------
# pop_delete.py -- Delete messages on a POP server by UID.
#
# Useful when you accidentally send yourself an email so malformed that
# fetchmail won't touch it.
#
# Copyright 2011 Michael Kelly (michael@michaelkelly.org)
#
# Mon Mar  7 23:45:24 EST 2011
# -----------------------------------------------------------------

import poplib
import logging
import sys
from optparse import OptionParser

logging.basicConfig(level=logging.INFO)

parser = OptionParser(usage='Usage: %prog [options] UIDs [...]')
parser.add_option('-u', dest='username',
                  help='POP3 username. Required.')
parser.add_option('-p', dest='password',
                  help='POP3 password. Required.')
parser.add_option('-s', dest='server',
                  help='POP3 server name. Required. Optionally, server:port.')

uids_to_delete = sys.argv[1:]

options, args = parser.parse_args()

if (not args or not options.username or not options.password or not
    options.server):
  parser.print_help()
  sys.exit(2)

uids_to_delete = args
if ':' in options.server:
  server, port = options.server.split(':', 1)
else:
  server = options.server
  port = 995

p = poplib.POP3_SSL(server, port)
p.set_debuglevel(2)

p.user(options.username)
p.pass_(options.password)
p.stat()

deleted = 0
l = p.uidl()
for message in l[1]:
  logging.info('Message: %s', message)
  num, uid = message.split(' ', 2)
  if uid in uids_to_delete:
    logging.info('Will delete: %s (%s)', uid, num)
    p.dele(num)
    deleted += 1

p.quit()
logging.info('Done. Deleted %d messages.', deleted)
