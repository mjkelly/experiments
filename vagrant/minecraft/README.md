Vagrant+Ansible Configs for Minecraft Server
============================================

This directory contains `Vagrantfile` (for Vagrant, http://vagrantup.com) and
`ansible-playbook` (for Ansible, http://ansibleworks.com) which set up a
virtual machine to run Minecraft.

When finished, you should have a `minecraft` user whose home directory
contains everything you need to start running a minecraft server. If you want
to start a brand new server, all you should need to do is call `./run.sh` to
start the server and whitelist your user. (`/whitelist add <username>` on the
minecraft server console.)

DISCLAIMER
----------
I wrote these as a way of learning Vagrant and Ansible and you absolutely
should not trust them. They are probably terrible. (That said, they work on my
machine.)

These are designed for the versions of Vagrant and Ansible available on Debian
testing (jessie): Vagrant v1.2.2 and Ansible v1.4.4. **These are actually
rather old.** There are notes about changes I *know* are necessary for
running with newer versions.

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

You should be up and running with just a few steps:

    host$ SSH_AUTH_SOCK= vagrant up
    $ vagrant ssh
    vagrant@precise32:~$ sudo su minecraft
    $ cd

Now you're in user `minecraft`'s home directory, which contains everything you
need for a fresh server. The simplest way to set up the server in an
easy-to-manage way is to put it in tmux (which is installed by default):

    $ tmux new
    $ ./run.sh

Once the server is running, be sure to whitelist yourself if you didn't turn
off the whitelist in `server.properties`:

    /whitelist add [minecraft user]

Things you may need to change
-----------------------------

Minecraft version! It is currently set to **1.7.4**. You can change it in
`ansible-playbook`.

IP address of the VM! It is hardcoded to **192.168.33.10**. You can change it
in `Vagrantfile`.

Minecraft port! It is set to the default port. You can change it in
`Vagrantfile`. Remember to update your SRV records:
http://wiki.multiplay.co.uk/Minecraft/Hostnames
