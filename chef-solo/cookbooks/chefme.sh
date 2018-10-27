#!/bin/bash

which chef-solo || sudo rpm -i https://packages.chef.io/files/stable/chefdk/3.3.23/el/7/chefdk-3.3.23-1.el7.x86_64.rpm

cd ~/cookbooks
sudo chef-solo -c solo.rb -j lockdown.json
