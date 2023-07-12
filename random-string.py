#!/usr/bin/python3
# -----------------------------------------------------------------
# random-string.py -- Generates a random printable string.
# Copyright 2013 Michael Kelly (michael@michaelkelly.org)
#
# Sat May  2 22:18:51 EDT 2020
# -----------------------------------------------------------------

import math
import random
import sys
import argparse

parser = argparse.ArgumentParser(
    description='Generate random printable strings.')
parser.add_argument(
    '--quiet',
    default=False,
    action='store_true',
    help='Suppress unnecessary output.')
parser.add_argument(
    '--alphanum',
    default=False,
    action='store_true',
    help='Only generate strings from alphanumeric characters. '
    'Mutually exclusive with --loweralphanum, --numeric.')
parser.add_argument(
    '--loweralphanum',
    default=False,
    action='store_true',
    help='Only generate strings from lowercase alphanumeric characters. '
    'Mutually exclusive with --alphanum, --numeric.')
parser.add_argument(
    '--numeric',
    default=False,
    action='store_true',
    help='Only generate strings from numbers. '
    'Mutually exclusive with --alphanum, --loweralphanum.')
parser.add_argument(
    'length',
    default=16,
    nargs='?',
    type=int,
    help='Number of characters in password.')
parser.add_argument(
    '--setting',
    default='default',
    choices=['default', 'chasebank'],
    help=("Use a particular set of special characters to satisfy password "
    "requirements. This just controls special characters for now, it doesn't "
    "cover repetition rules, etc."))
args = parser.parse_args()

chars_numeric = list('0123456789')
chars_loweralpha = list('abcdefghijklmnopqrstuvwxyz' '0123456789')
# This is included only if --loweralphanum is false.
chars_upperalpha = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

# This is included only if --alphanum and --loweralphanum are false.
# This list is a little restricted based on what I think will be reasonable to
# type on most keyboards. I'm skipping: $, which is US-centric. This isn't
# scientific; it's just guessing, based on me staring at my Thinkpad keyboard.
chars_symbols = list('~!@#%^&*()-_=+' '[]{}|;:<>,./?')

if args.setting == 'chasebank':
    chars_symbols = list('@!#$%+/=~')

if args.loweralphanum and args.alphanum:
    raise Exception('Cannot specify both --loweralphanum and --alphanum!')

password_length = args.length
if args.loweralphanum:
    chars = chars_loweralpha
elif args.alphanum:
    chars = chars_loweralpha + chars_upperalpha
elif args.numeric:
    chars = chars_numeric
else:
    chars = chars_loweralpha + chars_upperalpha + chars_symbols

bits_per_char = math.log(len(chars), 2)
total_bits = bits_per_char * password_length

if not args.quiet:
    print(f'{password_length} characters long.')
    print('Choosing from %d characters. %2.3f bits of entropy per character.' % (
        len(chars), bits_per_char))
    print('%2.3f total bits of entropy for password.' % total_bits)
    print('\nPassword:')

r = random.SystemRandom()

string = ''.join([r.choice(chars) for _ in range(password_length)])
print(string)
