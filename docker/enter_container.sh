#!/bin/bash
patt="$1"
nsenter --target $(docker inspect --format {{.State.Pid}} $(docker ps | grep "${patt}" | awk '{print $1}')) --mount --uts --ipc --net --pid
