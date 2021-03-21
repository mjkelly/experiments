# libvirt

These are my experiments with libvirt virtualization automation. It all assumes
a KVM backend.

## cloudinit-py

A helper I wrote to create and destroy VMs via libvirt CLI tools, backed by
LVM. It's designed to keep everything in its own namespace, so it can't delete
other VMs or logical volumes you've created. It supports custom VM sizing, and
adding a separate data disk.  

If I want to play with some new software, I use this tool to spin up a
throwaway VM run it on.

It includes a Makefile to help build it:
1. `make` makes a venv.
2. `make cloudinit-lvm.pyz` creates a zipapp, a self-contained binary (well, it
   still needs python3).

It has a few caveats:
1. It requires a little setup of global variables at the top, like the
   directory where you store your base images, names of volume groups, etc.
2. It's highly Linux-centric and probably can't spin up anything other than
   Ubuntu, Debian, and CentOS without some modification.

## borg-lvm-backup.sh

Takes snapshots of VMs that are backed by LVM and puts them in a borg archive.
LVM and borg do all the heavy lifting here!

## Old stuff

### cloudinit.sh

A quick way to make a VM from a cloudinit image.

### cloudinit-lvm.sh

This is a variation on cloudinit.sh that uses LVM for storage. The two scripts
should probably be merged in the future.

The two major dependencies are:

1. We expect an already-configured volume group in which to store our disk images.
2. We expect raw disk images, not qcow2 images. There are intsructions on how
   to do the conversion in the script.

