#
# Cookbook:: lockdown
# Recipe:: unattended-upgrades
#

cookbook_file '/etc/apt/apt.conf.d/20auto-upgrades' do
  source '/apt/20auto-upgrades'
  notifies :restart, 'service[unattended-upgrades]', :delayed
end

service 'unattended-upgrades' do
  action [:start, :enable]
  supports :reload => false, :restart => true, :status => true
end
