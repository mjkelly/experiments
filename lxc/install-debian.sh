#!/bin/bash
set -e
set -u

NAME=$1
source "$(dirname $0)/install-base.sh"

# Install and start container
lxc_create "$NAME" "debian" "bookworm" "amd64" "default"
lxc_start "$NAME"

# Very minimal and hacky provisioning
for script in provisioning/*; do
	echo -e "\n*** Running: ${script} ***"
	cat "${script}" | systemd_wrap lxc-attach "${NAME}" -- /bin/bash
done
