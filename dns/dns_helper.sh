#!/bin/bash
# This script abuses route53-update2.py and turns it into a general purpose
# route53 DNS helper. It's useful for manually managing a homelab domain.
# It only supports adding and deleting A records. For anything fancier, you'll
# have to use something real.

ENV_FILE=$HOME/.dns_helper_env

. "${ENV_FILE}"
export AWS_PROFILE

function usage() {
  echo "Usage:"
  echo "  $0 set <hostname> <ip>"
  echo "  $0 del <hostname>"
  echo
  echo "Sourcing ${ENV_FILE}..."
  echo "  DOMAIN=${DOMAIN}"
  echo "  ZONE=${ZONE}"
  echo "  AWS_PROFILE=${AWS_PROFILE}"
  exit 2
}

op=$1
cd ~/git/experiments/dns
if [[ $op = "set" ]]; then
  [[ $# -ne 3 ]] && usage
  name=$2
  ip=$3
  ./venv/bin/python3 ./route53-update2.py --zone-id="${ZONE}" --log-level INFO --domain "${name}.${DOMAIN}." --ip "${ip}" --ttl 120
elif [[ $op = "del" ]]; then
  [[ $# -ne 2 ]] && usage
  name=$2
  ./venv/bin/python3 ./route53-update2.py --zone-id="${ZONE}" --log-level INFO --delete --domain "${name}.${DOMAIN}."
else
  echo "Unknown operation: $op"
  usage
fi
