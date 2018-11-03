#
# Cookbook:: lockdown
# Recipe:: default
#

file '/etc/chef-lockdown' do
  content "Using lockdown chef recipe\n"
end

include_recipe 'lockdown::ufw'
include_recipe 'lockdown::ssh'
include_recipe 'lockdown::unattended-upgrades'
