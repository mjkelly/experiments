#
# Cookbook:: lockdown
# Recipe:: ssh
#

cookbook_file '/etc/ssh/sshd_config' do
  source 'sshd_config'
  notifies :reload, 'service[sshd]', :delayed
end

service 'sshd' do
  action [:start, :enable]
  supports :reload => true, :restart => true, :status => true
end
