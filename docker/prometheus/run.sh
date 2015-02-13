#!/bin/bash

# This is an example of how to run this docker image. This just maps both data
# and conf volumes to the docker host. You may wish to pass "-ti" instead of
# "-d" to run interactively.
docker run -d \
  --restart=always \
  -p 0.0.0.0:9090:9090 \
  -v $PWD/data:/data \
  -v $PWD/conf:/conf \
  prometheus:latest

