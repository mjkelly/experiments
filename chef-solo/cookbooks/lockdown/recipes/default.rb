#
# Cookbook:: lockdown
# Recipe:: default
#

file '/etc/chef-lockdown' do
  content "Using lockdown chef recipe\n"
end

include_recipe 'lockdown::epel'
include_recipe 'lockdown::yum-cron'
