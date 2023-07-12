#!/bin/bash
# -----------------------------------------------------------------
# apcms-powerctl.sh -- Controls outlets on an APC MasterSwitch via SNMP.
#
# This was written using the following references:
# - http://wiki.koshatul.com/APC_Master_Switch_SNMP_Control
# - ftp://ftp.apc.com/apc/public/software/pnetmib/mib/344/990-6052C.pdf
# - https://support.ipmonitor.com/mibs/POWERNET-MIB/info.aspx
#
# Copyright 2013 Michael Kelly (michael@michaelkelly.org)
#
# -----------------------------------------------------------------
# INSTRUCTIONS:
# - The MasterSwitch must be on your network, and have R/W SNMP access enabled.
# - You must fill in the MasterSwitch's IP address, and the name of its R/W
#   SNMP community below.
#
# -----------------------------------------------------------------
# CONFIGURATION:
# The default is 'private'.
community='private'
# The unit appears to use DHCP by default. (On my unit, the MAC address is
# listed on the underside of the AP9606 network card.)
address='10.1.1.100'
# -----------------------------------------------------------------
# Fri Mar 21 19:08:26 EDT 2014

# The integer after this prefix is the outlet number. Debian doesn't have a MIB
# file for APC MasterSwitch by default, so we just use the numeric values.
outlet_control_prefix='1.3.6.1.4.1.318.1.1.4.4.2.1.3.'

# According to PDF reference linked above, the valid values here are:
# 1 = outletOn
# 2 = outletOff
# 3 = outletReboot
# 5 = outletOnWithDelay
# 6 = outletOffWithDelay
# 7 = outletRebootWithDelay
#
# The default delay for rebooting (via the outletReboot action) appears to be 5
# seconds. It can be controlled on a per-outlet basis via the OID
# 1.3.6.1.4.1.318.1.1.4.5.2.1.5.1, .2, .3, etc (the last index corresponding to
# the outlet number).
ACTION_ON='1'
ACTION_OFF='2'
ACTION_REBOOT='3'

# Controls an outlet.
# Arguments:
# - Outlet number
# - Action number. Should be chosen from constants above.
control_outlet() {
  local outlet_index="$1"
  local action="$2"
  snmpset -v 1 -c "${community}" "${address}" "${outlet_control_prefix}${outlet_index}" i "${action}" >/dev/null || exit 1
}

# Prints usage info to stderr and exit.
usage_and_exit() {
  echo "Usage: $0 <OUTLET_NUMBER> on|off|reboot" >&2
  exit 2
}

if [ "$#" -ne 2 ]; then
  usage_and_exit
fi

outlet="$1"
case "$2" in
  on)
    control_outlet "${outlet}" $ACTION_ON || exit 1
  ;;
  off)
    control_outlet "${outlet}" $ACTION_OFF || exit 1
  ;;
  reboot)
    control_outlet "${outlet}" $ACTION_REBOOT || exit 1
  ;;
  *)
    usage_and_exit
  ;;
esac
