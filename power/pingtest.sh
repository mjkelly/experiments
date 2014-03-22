#!/bin/bash
# -----------------------------------------------------------------
# pingtest.sh -- Cycles power outlet if network connection test fails. The
# intended use is to restart a cable modem (or similar). This script logs its
# status to the system log. Configuration options are below.
#
# This script is designed to be run as a cron job. A decent configuration is to
# run this script every 30 minutes and set failure_threshold=2. This means it
# will take 30 minutes to detect a bad network, and the power won't be cycled
# more often than every 30 mins.
#
# This script accepts an "-n" option, which activates "dry run" mode -- the
# script takes no actions, but instead logs them to syslog.
#
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
# Tue Mar 11 21:32:32 EDT 2014
# -----------------------------------------------------------------
# CONFIGURATION:
# IP address outside the component you're testing. (E.g., if your power control
# script is hooked up to your router, this should be a reliable IP address
# external to your local network.)
test_ip='8.8.8.8'
# An IP address inside your network. If this is not reachable, we will not test
# the test IP and not register a failure. Default expression attempts to use
# the default gateway. It should be a fine value as long as it works.
local_ip="$(ip -4 route show 0/0 | awk '{print $3}')"
# How many successive tests must fail before we cycle power. (Consider this
# value combined with how often you are running this script to determine
# detection speed, and how frequently you may repeatedly cycle power.)
failure_threshold=2
# This function does the actual power cycling. Edit this if you have your own
# script to control power. (apcms-powerctl.sh controls power outlets on an APC
# MasterSwitch via SNMP.)
cycle_power() {
	~/power/apcms-powerctl.sh 8 reboot
}
# -----------------------------------------------------------------

hist_file="$HOME/.pingtest-hist"

if [ "$1" = "-n" ]; then
	dry_run='dry'
else
	dry_run=''
fi


syslog() {
	logger "pingtest: $1"
}

cycle_network() {
	if [[ "$1" == "dry" ]]; then
		syslog "Would restart network connection here, but dry run mode is on."
	else
		syslog "RESTARTING NETWORK CONNECTION"
		cycle_power
	fi
}

# Make sure the network is functional by testing an internal address.
ping -q -c 3 -w 10 "$local_ip" >/dev/null
if [[ "$?" != "0" ]]; then
	syslog "local IP address $local_ip isn't available; skipping test"
  echo "SKIPPED $test_ip @ $(date)" > "$hist_file"
  exit 0
fi

# Make multiple tries at pinging the test IP. This lets us try to ride out
# short disruptions. We don't want to trigger on an occasional dropped packet.
count=1
max_count=5
ping_success=0
while [[ "$count" -le "$max_count" ]]; do
	ping -q -c 1 -w 10 "$test_ip" >/dev/null

	if [[ "$?" == "0" ]]; then
    ping_success=1
    break
	fi
	count="$(($count + 1))"
done

if [[ "$ping_success" == 1 ]]; then
	syslog "success for $test_ip"
  echo "SUCCESS $test_ip @ $(date)" > "$hist_file"
else
	syslog "failed for $test_ip"
  echo "FAIL $test_ip @ $(date)" >> "$hist_file"
fi

lines="$(wc -l $hist_file | awk '{ print $1 }')"
# We check for strictly > failure_threshold because one line will be the last
# 'SUCCESS' message.
if [[ "$lines" > "$failure_threshold" ]]; then
  cycle_network "$dry_run"
fi
