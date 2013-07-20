#!/bin/bash
# -----------------------------------------------------------------
# usb-paranoia.sh -- Checks for unexpected new USB devices, by name.
#
# Mon Jul 15 17:01:52 EDT 2013
#
# If current USB devices differ from expected ones, the extras are printed to
# stderr, and this script returns 1. Otherwise it is silent and returns 0. The
# script strips out the IDs before comparing.
#
# Expected devices are stored in the file ~/.usb-paranoia-expected. You can set
# it to your current devices by running:
#
# lsusb > ~/.usb-paranoia-expected
#
# You can effectively "comment out" entries in this file by prefixing them with
# "#". (The "#" has no special meaning, but extra lines in this file are
# ignored if they don't match any existing devices, and lines starting with "#"
# will never match the output of lsusb(1).)
#
# This script was inspiring by an epic prank in which one of my coworkers
# surreptitiously added a new keyboard and mouse to another coworker's machine,
# and very occasionally moved the mouse or typed a single letter. (This script
# still relies on a file can be changed, but it raises the bar.)
# -----------------------------------------------------------------

# Change these if your lsusb is installed somewhere else.
LSUSB=/usr/bin/lsusb

EXPECTED_DEVICES="$HOME/.usb-paranoia-expected"
actual_tmp="$(mktemp usb-paranoia.XXXXXXXX)"

# This strips bus and device numbers from the lsusb output. Device numbers,
# specifically, can change when a device is disconnected and reconnected, so it
# makes no sense to show them as diffs.
function strip_ids() {
  perl -pe 's/^Bus \d+ Device \d+://;'
}

function print_extra_devices() {
  strip_ids < $EXPECTED_DEVICES | sort | \
      comm --check-order -1 -3 - $actual_tmp
}

if [[ ! -f "$EXPECTED_DEVICES" ]]; then
  echo "List of expected devices not found at $EXPECTED_DEVICES" >&2
  echo "Aborting." >&2
  exit 2
fi

$LSUSB | strip_ids | sort > $actual_tmp
if [[ -n "$(print_extra_devices)" ]]; then
  print_extra_devices
  return_value=1
else
  return_value=0
fi
# There's a chance we'll leak this file if something happens in the preceding
# lines. Whatever.
rm -f $actual_tmp

exit $return_value
