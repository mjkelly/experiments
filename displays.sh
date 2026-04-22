#!/bin/bash
# ***There is a python version of this script which is slightly better.***
# See `displays.py`.
#
# This script is designed for laptops running the Sway WM with a single
# external monitor, which may physically be on the left or right. This is an
# easy way to swap the orientation (which affects things like cursor movement
# between screens, and 'move workspace to output left', etc).
#
# This is meant to for quick ad-hoc configuration. If you move between a few
# stable setups, something like `kanshi` is probably better:
#   <https://git.sr.ht/~emersion/kanshi>
#
# Configure your main display by setting `MAIN_DISPLAY` below.
# 
# Move external monitor to the left of internal display:
#   displays.sh left
# Move external monitor to the right of internal display:
#   displays.sh right
# 
# Requires `swaymsg` and `jq`.
# 
# Copyright (c) 2023 Michael Kelly <m@michaelkelly.org>.
#
# CONFIGURATION:
# The name of your laptop's internal display.
MAIN_DISPLAY=eDP-1
# END OF CONFIGURATION

set -e
set -u
function usage() {
  echo "Usage: $0 <left|right|above>" >&2
  echo "       $0 <on|off>" >&2
  echo "- left|right|above moves second display to the left, to the right, or above main display." >&2
  echo "- on|off enables or disables second display." >&2
  exit 2
}

# Usage checks
if [[ $# -ne 1 ]]; then
  usage
fi
op=$1
if [[ $op != "left" && $op != "right" && $op != "above" && $op != "off" && $op != "on" ]]; then
  usage
fi

# Sanity checks
outputs_json=$(swaymsg -r -t get_outputs)
monitor_count=$(echo "${outputs_json}" | jq length)
if [[ $monitor_count -ne 2 ]]; then
  echo "You have ${monitor_count} display(s). This script only handles exactly 2. Aborting." >&2
  exit 1
fi
main_count=$(echo "${outputs_json}" |
  jq ".[] | select(.name == \"${MAIN_DISPLAY}\") | .name" | wc -l)
if [[ $main_count -ne 1 ]]; then
  echo "Found ${main_count} displays matching ${MAIN_DISPLAY}. This probably means MAIN_DISPLAY is misconfigured. Aborting." >&2
  exit 1
fi

# Gather display names and sizes
main_width=$(echo "${outputs_json}" |
  jq ".[] | select(.name == \"${MAIN_DISPLAY}\") | .current_mode.width")
ext_width=$(echo "${outputs_json}" |
  jq -r ".[] | select(.name != \"${MAIN_DISPLAY}\") | .current_mode.width")
ext_height=$(echo "${outputs_json}" |
  jq -r ".[] | select(.name != \"${MAIN_DISPLAY}\") | .current_mode.height")
ext_display=$(echo "${outputs_json}" |
  jq -r ".[] | select(.name != \"${MAIN_DISPLAY}\") | .name")

# Orient/enable/disable the displays
if [[ $op == left ]]; then
  swaymsg "output ${MAIN_DISPLAY} position \"${ext_width},0\",output ${ext_display} position \"0,0\""
  echo "Layout: [${ext_display}][${MAIN_DISPLAY}]"
elif [[ $op == right ]]; then
  swaymsg "output ${MAIN_DISPLAY} position \"0,0\",output ${ext_display} position \"${main_width},0\""
  echo "Layout: [${MAIN_DISPLAY}][${ext_display}]"
elif [[ $op == above ]]; then
  swaymsg "output ${MAIN_DISPLAY} position \"0,${ext_height}\",output ${ext_display} position \"0,0\""
  echo "Layout: [${ext_display}]"
  echo "        [${MAIN_DISPLAY}]"
elif [[ $op == off ]]; then
  swaymsg "output ${ext_display} disable"
  echo "${ext_display} ${op}"
elif [[ $op == on ]]; then
  swaymsg "output ${ext_display} enable"
  echo "${ext_display} ${op}"
fi
