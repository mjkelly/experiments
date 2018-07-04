#!/bin/bash

. settings.env

build_pkg
aws lambda create-function \
  --region $region \
  --function-name $fname \
  --zip-file fileb://./pkg.zip \
  --role $role \
  --handler $handler \
  --runtime python2.7 \
  --profile $profile 
