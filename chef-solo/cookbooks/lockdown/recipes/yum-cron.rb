#
# Cookbook:: lockdown
# Recipe:: yum-cron
#

package 'yum-cron'

template '/etc/yum/yum-cron.conf' do
  source 'yum-cron.conf.erb'
end

service 'yum-cron' do
  action [:start, :enable]
end

