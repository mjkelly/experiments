#
# Cookbook:: lockdown
# Recipe:: ssh
#

cookbook_file '/etc/ufw/user.rules' do
  source 'ufw/user.rules'
  notifies :run, 'execute[ufw_reload]', :delayed
end

execute 'ufw_enable' do
  command 'ufw --force enable'
  only_if 'ufw status | grep inactive'
end

execute 'ufw_reload' do
  command 'ufw reload'
  action :nothing
end
