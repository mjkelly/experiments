#!/bin/bash
# This script checks the network connection of this machine, and cycles outlet
# power if the network check fails. The intended use is to restart a cable
# modem (or similar).
#
# This script logs is status to the system log.
#
# For configuration, see $test_ip, $powerctl, $dry_run.
#
# Michael Kelly <m@michaelkelly.org>
# Tue Mar 11 21:32:32 EDT 2014

# IP address to test. If your power outlet control script is connected to your
# router, this should be a reliable IP address outside your local network.
test_ip='8.8.8.8'
# This is a program that should accept args "off" and "on". This script was
# tested with <http://emergent.unpythonic.net/01330399156>. Beware that the
# program listed there requires root privileges (or special udev rules) to run.
powerctl=~root/power-outlet-ctl
# Set this to "dry" to only print a message to syslog, not actually cycle
# power. To actually cycle power, set it to the empty string.
dry_run="dry"

function syslog() {
	logger "pingtest: $1"
}

function cycle_network() {
	if [[ "$1" == "dry" ]]; then
		syslog "Would restart network connection here, but dry run mode is on."
	else
		syslog "RESTARTING NETWORK CONNECTION"
		$powerctl off
		sleep 5
		$powerctl on
	fi
}

# We test multiple times and only power cycle if every try fails. This way, we
# try to avoid falsely triggering on network congestion (which sucks, but won't
# be fixed by rebooting the router).
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
cycle_network $dry_run
