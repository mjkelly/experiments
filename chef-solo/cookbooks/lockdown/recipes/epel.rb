#
# Cookbook:: lockdown
# Recipe:: epel
#

if platform_family?('amazon')
  package "epel-release" do
    source 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm'
    action :install
    provider Chef::Provider::Package::Rpm
  end
elsif platform_family?('rhel')
  yum_package 'epel-release'
end
