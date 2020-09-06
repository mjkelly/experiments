#!/bin/bash
. "$(dirname $0)/env"
arduino-cli compile -b "${arduino_fqbn}" "$1"
