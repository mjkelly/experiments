#!/bin/bash
set -e
set -u

if [[ $# -ne 1 ]]; then
	echo "Usage: $0 <cookbook_name>"
	exit 2
fi

cookbook=$1
sudo chef-solo -c solo.rb -j cookbooks/$cookbook/$cookbook.json
