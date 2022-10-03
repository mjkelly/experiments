.PHONY: packer
packer: cidata.img
	PACKER_LOG=1 packer build cloudinit-ubuntu.json

cidata.img: user-data meta-data
	genisoimage -output cidata.img -volid cidata -joliet -rock user-data meta-data

.PHONY: clean
clean:
	rm -rf cidata.img packer-out
