/usr/bin/qemu-system-x86_64 \
  -m 512M \
  -name packer-deb1 \
  -boot c \
  -netdev user,id=user.0,hostfwd=tcp::2253-:22 \
  -vnc 127.0.0.1:81 \
  -display gtk \
  -drive file=./packer-out/cloudinit1,if=virtio,cache=writeback,discard=ignore,format=qcow2 \
  -device virtio-net,netdev=user.0 \
  -machine type=pc,accel=kvm

