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

    host$ vagrant up
    [the ansible step may take quite some time, as it updates all packages to their
    latest versions]
    $ vagrant ssh
    vagrant@precise32:~$ sudo su minecraft
    $ tmux new
    $ ./run.sh
    /whitelist add [minecraft user]
