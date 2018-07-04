#!/bin/bash

. settings.env

aws lambda invoke \
--invocation-type RequestResponse \
--function-name $fname \
--region $region \
--payload file://./input.json \
--profile $profile \
output
rc=$?
if [[ "$rc" == 0 ]]; then
  echo "output:"
  jq . < output
  #cat output | jq .
  echo
fi
