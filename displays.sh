#!/bin/bash
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
  echo "Usage: $0 <left|right>" >&2
  echo "Moves second display to the left or right of main display." >&2
  exit 2
}

# Usage checks
if [[ $# -ne 1 ]]; then
  usage
fi
pos=$1
if [[ $pos != "left" && $pos != "right" ]]; then
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
ext_display=$(echo "${outputs_json}" |
  jq -r ".[] | select(.name != \"${MAIN_DISPLAY}\") | .name")

# Orient the displays
if [[ $pos == left ]]; then
  swaymsg "output ${MAIN_DISPLAY} position \"${ext_width},0\",output ${ext_display} position \"0,0\""
elif [[ $pos == right ]]; then
  swaymsg "output ${MAIN_DISPLAY} position \"0,0\",output ${ext_display} position \"${main_width},0\""
fi
echo "${ext_display} ${pos} of main display ${MAIN_DISPLAY}"
