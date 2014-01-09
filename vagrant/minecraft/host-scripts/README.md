Host Scripts
============

These are scripts you can use on the host machine.

server-backup.sh
----------------
This script copies the contents of the `~minecraft` directory to the local
machine. It should work without modification.

minecraft-vm
------------

This is a SysV init script that starts the minecraft VM when the host machine
boots, and stops it when the host machine shuts down. (You may notice that your
machine won't shut down until you stop the VM because the network device is in
use. This script was created as a workaround for that.)

The script requires some setup:

   * Edit `user` the variable. This should be the user you started your VM as.
     The init script will run all VirtualBox commands as this user.
   * Edit the `vm_id` variable. This should be the unique ID of the VM that
     Vagrant created when you ran `vagrant up`. You can list all running VMs
     with: `VBoxManage list vms`
   * Copy the script to /etc/init.d.
   * Install the script by running: `update-rc.d minecraft-vm enable`. This
     will ensure that it starts and stops properly.
