#!/usr/bin/env python3
# This script is designed for laptops running the Sway WM with a single
# external monitor, which may physically be on the left, right, or above your
# built-in display. This is an easy way to swap the orientation.
#
# This is a python version of `displays.sh`.
#
# This is meant to for quick ad-hoc configuration. If you move between a few
# stable setups, something like `kanshi` is probably better:
#   <https://git.sr.ht/~emersion/kanshi>
#
# Configure your main display by setting `MAIN_DISPLAY` below.
#
# Requires: swaymsg(1)
#
# Copyright (c) 2023 Michael Kelly <m@michaelkelly.org>.

# CONFIGURATION:
# The name of your laptop's internal display.
MAIN_DISPLAY = "eDP-1"
# END OF CONFIGURATION

import argparse
import json
import subprocess
import sys


def swaymsg(*args):
    return subprocess.run(["swaymsg"] + list(args),
                          check=True,
                          capture_output=True,
                          text=True).stdout


def get_outputs():
    return json.loads(swaymsg("-r", "-t", "get_outputs"))


def op_left(main, ext):
    ext_name = ext["name"]
    ext_width = ext["current_mode"]["width"]
    swaymsg(
        f'output {MAIN_DISPLAY} position "{ext_width},0",output {ext_name} position "0,0"'
    )
    print(f"Layout: [{ext_name}][{MAIN_DISPLAY}]")


def op_right(main, ext):
    ext_name = ext["name"]
    main_width = main["current_mode"]["width"]
    swaymsg(
        f'output {MAIN_DISPLAY} position "0,0",output {ext_name} position "{main_width},0"'
    )
    print(f"Layout: [{MAIN_DISPLAY}][{ext_name}]")


def op_above(main, ext):
    ext_name = ext["name"]
    ext_height = ext["current_mode"]["height"]
    swaymsg(
        f'output {MAIN_DISPLAY} position "0,{ext_height}",output {ext_name} position "0,0"'
    )
    print(f"Layout: [{ext_name}]")
    print(f"        [{MAIN_DISPLAY}]")


def op_off(main, ext):
    ext_name = ext["name"]
    swaymsg(f"output {ext_name} disable")
    print(f"{ext_name} off")


def op_on(main, ext):
    ext_name = ext["name"]
    swaymsg(f"output {ext_name} enable")
    print(f"{ext_name} on")


def main():
    parser = argparse.ArgumentParser(
        description="Position or toggle an external Sway display.")
    parser.add_argument(
        "op",
        choices=["left", "right", "above", "on", "off"],
        help=
        "Move the external display left/right/above the main display, or turn it on/off.",
    )
    args = parser.parse_args()
    op = args.op

    # Sanity checks
    outputs = get_outputs()
    if len(outputs) != 2:
        print(
            f"You have {len(outputs)} display(s). This script only handles exactly 2. Aborting.",
            file=sys.stderr)
        sys.exit(1)

    main_displays = [o for o in outputs if o["name"] == MAIN_DISPLAY]
    if len(main_displays) != 1:
        print(
            f"Found {len(main_displays)} displays matching {MAIN_DISPLAY}. This probably means MAIN_DISPLAY is misconfigured. Aborting.",
            file=sys.stderr)
        sys.exit(1)

    # Gather display names and sizes
    main = main_displays[0]
    ext = next(o for o in outputs if o["name"] != MAIN_DISPLAY)

    # we must enable the external display before doing anything else
    if not ext["active"] and op != "on":
        op_on(main, ext)

    ops = {
        "left": op_left,
        "right": op_right,
        "above": op_above,
        "off": op_off,
        "on": op_on
    }
    ops[op](main, ext)


if __name__ == "__main__":
    main()
