#!/bin/bash
# -----------------------------------------------------------------
# pingtest.sh -- Cycles power outlet if network connection test fails. The
# intended use is to restart a cable modem (or similar). This script logs its
# status to the system log.
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
# IP address to test. If your power outlet control script is connected to your
# router, this should be a reliable IP address outside your local network.
test_ip='8.8.8.8'
# This function does the actual power cycling. Edit this if you have your own
# script to control power. (apcms-powerctl.sh controls power outlets on an APC
# MasterSwitch via SNMP.)
cycle_power() {
	~/power/apcms-powerctl.sh 1 reboot
}
# -----------------------------------------------------------------


if [ "$1" = "-n" ]; then
	dry_run=1
else
	dry_run=0
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

count=1
max_count=3
while [[ "$count" -le "$max_count" ]]; do
	ping -q -c 3 -w 10 "$test_ip" >/dev/null

	if [[ "$?" == "0" ]]; then
		syslog "success; exiting"
		exit 0
	else
		syslog "ping failed ($count/$max_count)"
	fi
	count="$(($count + 1))"
done

if [ "$dry_run" = 1 ]; then
  cycle_network dry
  exit 1
else
  cycle_network
  exit 1
fi
