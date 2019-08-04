# cloud-init LVM

This is a variation on cloudinit.sh that uses LVM for storage. The two scripts
should probably be merged in the future.

The two major dependencies are:

1. We expect an already-configured volume group in which to store our disk images.
2. We expect raw disk images, not qcow2 images. There are intsructions on how
   to do the conversion in the script.
