# libvirt

These are my experiments with libvirt virtualization automation. It all assumes
a KVM backend.

## cloudinit.sh

A quick way to make a VM from a cloudinit image.

## cloudinit-lvm.sh

This is a variation on cloudinit.sh that uses LVM for storage. The two scripts
should probably be merged in the future.

The two major dependencies are:

1. We expect an already-configured volume group in which to store our disk images.
2. We expect raw disk images, not qcow2 images. There are intsructions on how
   to do the conversion in the script.

## borg-lvm-backup.sh

Takes snapshots of VMs that are backed by LVM and puts them in a borg archive.
LVM and borg do all the heavy lifting here!
