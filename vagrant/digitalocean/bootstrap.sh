#!/bin/bash
apt-get update
apt-get install -y git
git clone https://github.com/mjkelly/config.git && \
  cd config && \
  ./deploy.sh real
