#!/bin/bash
# This script updates a specific domain name in route53. It is designed to be
# run via crontab. The underlying update script will not push changes unless
# there is a change in the IP.
#
# Michael Kelly
# Thu Jan 17 13:09:29 EST 2013

# == Amazon config and authentication ==
# You can find the zone information in your route53 dashboard, and the
# authentication information under "My Account / Console" -> "Security
# Credentials".
domain="ADDME"
zone_id="ADDME"
key_id="ADDME"
key_secret="ADDME"

# == How to get current IP ==
# There is no reason to change this unless the given server changes.
ip_server="http://ipv4.icanhazip.com"
current_ip="$(curl --silent ${ip_server})"

# == Update script ==
# Change the path to the route53-update script if necessary.
update_cmd="./route53-update.py"

${update_cmd} \
  --domain="${domain}" \
  --zone-id="${zone_id}" \
  --amz-key-id="${key_id}" \
  --amz-key-secret="${key_secret}" \
  --ip="${current_ip}"
exit $?
