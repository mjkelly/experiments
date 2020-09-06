#!/bin/bash
. "$(dirname $0)/env"
stty 9600 -F "${arduino_tty}" raw -echo && cat "${arduino_tty}"
