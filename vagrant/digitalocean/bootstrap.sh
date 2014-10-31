#!/bin/bash
cd $HOME
sudo apt-get update
sudo apt-get install -y git
(test -d config || git clone https://github.com/mjkelly/config.git) && \
  cd config && ./deploy.sh config && ./deploy.sh packages
