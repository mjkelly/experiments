.PHONY: packer
packer: cidata.img
	PACKER_LOG=1 packer build cloudinit-ubuntu.json

cidata.img: user-data meta-data
	genisoimage -output cidata.img -volid cidata -joliet -rock user-data meta-data

mount:
	mkdir ./mnt
	guestmount -a packer-out/cloudinit1 -i --ro ./mnt

unmount:
	umount ./mnt
	rmdir ./mnt

.PHONY: clean
clean:
	rm -rf cidata.img packer-out
