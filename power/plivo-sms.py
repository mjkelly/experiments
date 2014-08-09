#!/usr/bin/env python
# This is based on plivo's sample, from here:
# https://github.com/plivo/plivo-examples-python/blob/master/plivo_message.py
#
# I'm using this to alert me when my UPS goes on and off of battery.
#
# Prereqs:
# apt-get install python-pip
# pip install flask plivo

import os
import sys
import datetime

import plivo

# Get message to send, or raise an exception if user didn't provide one.
text = sys.argv[1]

# Your PLIVO_AUTH_ID and PLIVO_AUTH_TOKEN can be found on your Plivo Dashboard https://manage.plivo.com/dashboard
PLIVO_AUTH_ID = 'ADDME'
PLIVO_AUTH_TOKEN = 'ADDME'
# Enter your Plivo phone number. This will show up on your caller ID
plivo_number = 'ADDME'
# Enter the phone number that you would like to receive your SMS
destination_number = 'ADDME' # google voice

message_params = {
    'src': plivo_number,
    'dst': destination_number,
    'text': text,
}
p = plivo.RestAPI(PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN)
now = datetime.datetime.now()
resp = p.send_message(message_params)

with open(os.getenv('HOME') + '/plivo-sms.log', 'a') as fh:
    print >>fh, '{time} {response}'.format(time=now, response=resp)
