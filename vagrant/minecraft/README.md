Vagrant+Ansible Configs for Minecraft Server
============================================

This directory contains `Vagrantfile` (for Vagrant, http://vagrantup.com) and 
`ansible-playbook` (for Ansible, http://ansibleworks.com) which set up a
virtual machine to run Minecraft.

When finished, you should have a `minecraft` user whose home directory
contains a minecraft server directory. The server should be running under mark2
(https://github.com/mcdevs/mark2), though note that unless you edited the 
`white-list.txt` under `files/default-server`, you must add users to the 
whitelist before anyone can join.



DISCLAIMER
----------
I wrote these as a way of learning Vagrant and Ansible and you absolutely
should not trust them. They are probably terrible. (That said, they work on my
machine.)

These are designed for the versions of Vagrant and Ansible available on Debian
testing (jessie): Vagrant v1.2.2 and Ansible v1.4.4. **These are actually
rather old.**

Changes I'm aware of for running with newer versions:

  * New versions of the Ansible plugin for Vagrant use `inventory_path` instead of `inventory_file`. Update the reference in Vagrantfile.

Implementation Info
-------------------

The provided Vagrantfile uses the default _virtualbox_ provider. (It does
nothing fancy, however, and should be simple to adapt to other machines.)

The machine image is _precise32_ (because that was the default). It should be
readily adaptable to other Ubuntu or Debian versions; however, it will require
some modification to work with other distributions with different package
managers.

There is a provided minecraft `server.properties` file -- modify it if you
want. **The server allows only whitelisted users by default.**

Instructions
------------

Edit `files/default-server/white-list.txt` to include your minecraft username.
Otherwise you will not be able to join the server.

See "Options" below for configuration options you may want to set. If you're satisfied with setting up a fresh throwaway server, just continue.

All you have to do now is type `vagrant up`. Type `SSH_AUTH_SOCK= vagrant up` if you're running an ssh-agent, so your agent doesn't confuse ansible when it tries to ssh in. 

If you want to use an existing server, put your server directory somewhere on
your local machine, and set `minecraft_server_path` to the path to the server
directory.


Options
-------

There are configuration values in `minecraft-vars.yml` that you may want to change.


IP address of the VM is hardcoded to **192.168.33.10**. You can change it
in `Vagrantfile`. If you change it there, you must update it in `ansible-playbook` as well.

To change the port the server runs on, you must update the minecraft port in both `files/default-server/server.properties` (to change the port the server listens on) and `Vagrantfile` (to change the port forwarding from the host machine).

TODO: Make it easier to change the minecraft server port.
