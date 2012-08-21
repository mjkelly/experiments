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

import base64
import hashlib
import hmac
import httplib
import libxml2
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
opts, _ = parser.parse_args()

def usage():
  print '--amz-key-id, --amz-key-secret, --domain, --zone-id, and --ip are REQUIRED.'
  parser.print_help()
  sys.exit(2)

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
  return (response.getheader('Date'), ip)

def make_auth(time_str, key_id, secret):
  """Creates an amazon authorization string.

  Format is specified here:
  http://docs.amazonwebservices.com/Route53/latest/DeveloperGuide/RESTAuthentication.html#AuthorizationHeader
  """
  h = hmac.new(secret, time_str, hashlib.sha256)
  h_b64 = base64.b64encode(h.digest())
  return 'AWS3-HTTPS AWSAccessKeyId=%s,Algorithm=HmacSHA256,Signature=%s' % (
      key_id, h_b64)

def get_old_record_values(doc):
  """Returns the old values of the record we will update.

  Args:
    doc: the XML document of the existing record (just a single
        ResourceRecord), as a string.

  Returns:
    (ip, TTL): the IP and TTL of the existing record
  """
  # TODO(mjkelly): Consider just grabbing the content of <ResourceRecords>
  # verbatim so we can put it in the delete part of our request.
  xmldoc = libxml2.parseDoc(doc)
  context = xmldoc.xpathNewContext()
  context.xpathRegisterNs('aws',
      'https://route53.amazonaws.com/doc/2012-02-29/')
  values = context.xpathEval(
      '//aws:ResourceRecordSet/aws:ResourceRecords/aws:ResourceRecord/aws:Value')
  if not values:
    return (None, None)
  ttls = context.xpathEval(
      '//aws:ResourceRecordSet/aws:TTL')
  if not ttls:
    return (None, None)

  # TODO(mjkelly): I think there's some resource-freeing that I'm not doing
  # here.
  return (values[0].content, ttls[0].content)

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

# Check for all required args.
if (not opts.key_id or not opts.key_secret or not opts.domain or
    not opts.zone_id or not opts.ip):
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

print 'Will set %s to %s' % (domain, new_ip)

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
connection.request('GET', get_rrset_path, '', headers)
response = connection.getresponse()
old_ip, old_ttl = get_old_record_values(response.read())
if old_ip is None:
  raise RuntimeError('Previous IP for A record does not exist or is not parseable.')

if old_ip == new_ip:
  print 'Old IP %s is same as new IP. Quitting.' % old_ip
  sys.exit(0)

connection = httplib.HTTPSConnection('route53.amazonaws.com')
change_body = body.format(name=domain,
                          old_value=old_ip,
                          old_ttl=old_ttl,
                          new_value=new_ip,
                          new_ttl=300)
connection.request('POST', change_rrset_path, change_body, headers)
response = connection.getresponse()
print 'Response: %s' % response.read()
