#!/usr/bin/python
# -----------------------------------------------------------------
# route53-update.py -- Updates a DNS record in Amazon's Route 53.
#
# See documentation here:
# http://docs.amazonwebservices.com/Route53/2012-02-29/DeveloperGuide/RESTRequests.html
#
# Copyright 2012 Michael Kelly (michael@michaelkelly.org)
#
# This program is released under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Mon Aug 20 03:42:03 EDT 2012
# -----------------------------------------------------------------

from xml.etree import ElementTree
import base64
import hashlib
import hmac
import httplib
import optparse
import sys

parser = optparse.OptionParser()
parser.add_option('--amz-key-id', dest='key_id',
                  help='Amazon API key ID. Required.')
parser.add_option('--amz-key-secret', dest='key_secret',
                  help='Amazon API key secet value. Required.')
parser.add_option('--domain', dest='domain',
                  help='Domain name to update. Required.')
parser.add_option('--zone-id', dest='zone_id',
                  help='Amazon zone ID containing domain name. Required.')
parser.add_option('--ip', dest='ip', help='New IPv4 for domain name, or '
                  '"auto" to attempt to auto-detect. "auto" does not work '
                  'from behind a NAT. Required.')
parser.add_option('--quiet', '-q', dest='quiet', default=False,
                  action="store_true",
                  help="Don't output to stdout unless there is an error.")
parser.add_option('--verbose', '-v', dest='verbose', default=False,
                  action="store_true",
                  help="Output more information.")
parser.add_option('--force', '-f', dest='force', default=False,
                  action="store_true",
                  help="Update the A record even if it has not changed.")
opts, _ = parser.parse_args()

def usage():
  parser.print_help()
  sys.exit(2)

def log(msg):
  """Print unless we're in quiet mode."""
  if not opts.quiet:
    print msg

def vlog(msg):
  """Print if we're in verbose mode."""
  if opts.verbose:
    print msg

def get_time_and_ip():
  """Gets the current time from amazon servers.

  Also saves the IP address of the socket it uses to make the request. These
  two bits of functionality are bundled because the IP comes for free from the
  socket we use to get the date, and we might need the IP later.

  Format is RFC 1123.
  http://docs.amazonwebservices.com/Route53/latest/DeveloperGuide/RESTAuthentication.html#StringToSign

  Returns:
    (date, ipaddr)
  """
  connection = httplib.HTTPSConnection('route53.amazonaws.com')
  connection.request('GET', '/date')
  response = connection.getresponse()
  ip = connection.sock.getsockname()[0]
  return response.getheader('Date'), ip

def make_auth(time_str, key_id, secret):
  """Creates an amazon authorization string.

  Format is specified here:
  http://docs.amazonwebservices.com/Route53/latest/DeveloperGuide/RESTAuthentication.html#AuthorizationHeader
  """
  h = hmac.new(secret, time_str, hashlib.sha256)
  h_b64 = base64.b64encode(h.digest())
  return 'AWS3-HTTPS AWSAccessKeyId=%s,Algorithm=HmacSHA256,Signature=%s' % (
      key_id, h_b64)

def get_old_record_values(doc, name):
  """Returns the old values of the record we will update.

  Args:
    doc: the XML document of the existing record (just a single
        ResourceRecord), as a string.
    name: The name of the record (domain name) to update.

  Returns:
    (ip, TTL): the IP and TTL of the existing record
  """
  # TODO(mjkelly): This method could really use some tests.
  root = ElementTree.fromstring(doc)
  NS = '{https://route53.amazonaws.com/doc/2012-02-29/}'

  # TODO(mjkelly): Consider just grabbing the content of <ResourceRecords>
  # verbatim so we can put it in the delete part of our request. ElementTree
  # doens't print out the XML tree like it comes in, though -- I don't know if
  # Route 53 will understand it. 
  for child in root.iter(NS + 'ResourceRecordSet'):
    rec_type = child.find(NS + 'Type')
    rec_ttl = child.find(NS + 'TTL')
    rec_name = child.find(NS + 'Name')
    rec_values = list(child.iter(NS + 'Value'))

    if rec_type is None or rec_ttl is None or rec_name is None:
      raise ValueError('Cannot find all required elements: Type, Name, TTL.')
    if rec_type.text != 'A':
      raise ValueError('Bad record type %s (must be "A")' % rec_type.text)
    if len(rec_values) != 1:
      raise ValueError(
          'Can only update resource record with exactly one A value.')
    rec_type, rec_ttl, rec_name = rec_type.text, rec_ttl.text, rec_name.text
    rec_value = rec_values[0].text

    vlog('Found record %s: type=%s, name=%s, values=%s' % (
      child.tag, rec_type, rec_name, rec_value))
    if rec_name != name:
      vlog('Still looking for record %s...' % name)
      continue

    return rec_value, rec_ttl

  raise ValueError('Could not find existing A record for %s' % name)

# Format string for updating an A record, {name}, from {old_value} with
# {old_ttl} to {new_value} with {new_ttl}.
# See:
# http://docs.amazonwebservices.com/Route53/latest/APIReference/API_ChangeResourceRecordSets.html
body = """<?xml version="1.0" encoding="UTF-8"?>
<ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2012-02-29/">
   <ChangeBatch>
      <Comment>Automatic hostname update from route53-update.py.</Comment>
      <Changes>
         <Change>
            <Action>DELETE</Action>
            <ResourceRecordSet>
               <Name>{name}</Name>
               <Type>A</Type>
               <TTL>{old_ttl}</TTL>
               <ResourceRecords>
                  <ResourceRecord>
                     <Value>{old_value}</Value>
                  </ResourceRecord>
               </ResourceRecords>
            </ResourceRecordSet>
         </Change>
         <Change>
            <Action>CREATE</Action>
            <ResourceRecordSet>
               <Name>{name}</Name>
               <Type>A</Type>
               <TTL>{new_ttl}</TTL>
               <ResourceRecords>
                  <ResourceRecord>
                     <Value>{new_value}</Value>
                  </ResourceRecord>
               </ResourceRecords>
            </ResourceRecordSet>
         </Change>
      </Changes>
   </ChangeBatch>
</ChangeResourceRecordSetsRequest>
"""

# ========== main ==========

if (not opts.key_id or not opts.key_secret or not opts.domain or
    not opts.zone_id or not opts.ip):
  print >>sys.stderr, ('-amz-key-id, --amz-key-secret, --domain, --zone-id, '
                       'and --ip are required.\n')
  usage()
if opts.quiet and opts.verbose:
  print >>sys.stderr, '--quiet and --verbose are mutually exclusive.'
  usage()

time_str, default_iface_ip = get_time_and_ip()
key_id = opts.key_id
secret = opts.key_secret
zone_id = opts.zone_id
domain = opts.domain
if opts.ip == "auto":
  new_ip = default_iface_ip
else:
  new_ip = opts.ip

vlog('Will set %s to %s' % (domain, new_ip))

auth = make_auth(time_str, key_id, secret)
headers = {
  'X-Amz-Date': time_str,
  'X-Amzn-Authorization': auth,
}
# Path for GET request to list existing record only.
get_rrset_path = '/2012-02-29/hostedzone/%s/rrset?name=%s&type=A&maxitems=1' % (zone_id, domain)
# Path for POST request to update record.
change_rrset_path = '/2012-02-29/hostedzone/%s/rrset' % zone_id

connection = httplib.HTTPSConnection('route53.amazonaws.com')
vlog('GET %s' % get_rrset_path)

connection.request('GET', get_rrset_path, '', headers)
response = connection.getresponse()
response_txt = response.read()
vlog('Response:\n%s' % response_txt)

old_ip, old_ttl = get_old_record_values(response_txt, domain)
if old_ip is None:
  raise RuntimeError('Previous IP for A record does not exist or is not parseable.')

if old_ip == new_ip and not opts.force:
  vlog('Old IP %s is same as new IP. Quitting.' % old_ip)
  sys.exit(0)
else:
  log('Updating %s to %s (was %s)' % (domain, new_ip, old_ip))

connection = httplib.HTTPSConnection('route53.amazonaws.com')
change_body = body.format(name=domain,
                          old_value=old_ip,
                          old_ttl=old_ttl,
                          new_value=new_ip,
                          new_ttl=old_ttl)
vlog('POST %s\n%s' % (change_rrset_path, change_body))

connection.request('POST', change_rrset_path, change_body, headers)
response = connection.getresponse()
vlog('Response:\n%s' % response.read())
