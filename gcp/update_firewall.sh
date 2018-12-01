#!/bin/bash
# Helper to update my "allow all from home" firewall rule in GCP. We specify
# the name of the rule to update in the config file.
#
# We only update source-range, so the details of the rule are totally up to you
# (but you must create the rule yourself initially). This script won't change
# which ports the rule allows or which VMs it applies to.
#
# We expect the source range to be *exactly* the IP we get; we are not smart
# about CIDR ranges.

# We get $project and $rulename here.
source update_firewall_config.localonly
if [[ -z $project ]]; then
  echo '$project not defined in config file'
fi
if [[ -z $rulename ]]; then
  echo '$rulename not defined in config file'
fi

function gcp_fw() {
  gcloud --project="${project}" compute firewall-rules "$@"
}

# We pass -r to jq here to remove quotes, because we may need the actual IP
# address later.
ip="$(curl -s https://jsonip.com | jq -r .ip)"
echo "ip=$ip"
# We leave the quotes in here, because we just use this for string comparision.
ranges="$(gcp_fw describe "${rulename}" --format=json | jq .sourceRanges[])"
echo "ranges=$ranges"

# $ranges has quotes surrounding it $ip does not -- we add them. This is to
# avoid considering 192.168.1.1 == 192.168.1.100!
if echo "$ranges" | grep "\"$ip\"" >/dev/null; then
  echo "$ip is allowed, ok."
  exit 0
fi

echo "IP not in range; updating rule $rulename..."
gcp_fw update "${rulename}" --source-ranges="${ip}"
echo Done
