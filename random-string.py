#!/usr/bin/python
# -----------------------------------------------------------------
# random-string.py -- Generates a random printable string.
# Copyright 2013 Michael Kelly (michael@michaelkelly.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Thu Aug 29 00:01:30 EDT 2013
# -----------------------------------------------------------------

import math
import random
import sys
import argparse

parser = argparse.ArgumentParser(description='Generate random printable strings.')
parser.add_argument('--alphanumeric', default=False, action='store_true',
                    help='only generate strings from alphanumeric characters')
parser.add_argument('length', default=16, type=int,
                    help='Number of characters in password.')
args = parser.parse_args()

chars_alphanumeric = list(
  'abcdefghijklmnopqrstuvwxyz'
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  '0123456789'
)

# This list is a little restricted based on what I think will be reasonable to
# type on most keyboards. I'm skipping: `$'"
# This isn't scientific; it's just guessing.
chars_extra = list(
  '~!@#%^&*()-_=+'
  '[]{}|;:<>,./?'
)

password_length = args.length
if args.alphanumeric:
  chars = chars_alphanumeric
else:
  chars = chars_alphanumeric + chars_extra

bits_per_char = math.log(len(chars), 2)
total_bits = bits_per_char * password_length
print 'Choosing from %d characters. %2.3f bits of entropy per character.' % (len(chars), bits_per_char)
print '%d characters long.' % password_length
print '%2.3f total bits of entropy for password.' % total_bits

r = random.SystemRandom()

string = ''.join([r.choice(chars) for _ in xrange(password_length)])
print string
