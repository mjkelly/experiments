#!/bin/bash

. settings.env

build_pkg
aws lambda update-function-code \
  --publish \
  --function-name $fname \
  --zip-file fileb://./pkg.zip \
  --profile $profile 
