#!/bin/bash
. "$(dirname $0)/env"
arduino-cli upload -p "${arduino_tty}" -b "${arduino_fqbn}" "$1"
