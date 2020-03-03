# node-exporter

Installs and configures node-exporter. It even tries to open port 9100 on the
firewall if running on CentOS. This is a very rough sketch of a playbook!  It
works for me but may not work for you. (Also, I am a total Ansible noob.)

Make a copy of `hosts.example` that includes the hosts you want to configure.
This requires a user with passwordless sudo by default. (It uses
`ansible_become`.)

## Configuration

Check `group_vars/all.yml` for config options.

## Running

Assuming you created a file named `hosts`, run this:

```
ansible-playbook -i hosts node-exporter.yml
```
