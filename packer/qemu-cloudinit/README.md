# packer/qemu-cloudinit

This is a local packer setup that uses a qemu builder. We build cloudinit
images because they are, in my opinion, the simplest way to do no-touch
provisioning.

This is designed for experimentation. We set a short, insecure password on the
default user! (Though we do not allow password login over ssh.)

## Setup

This is one-time setup you'll need to do for authentication:

- We look for a key in `~/.ssh/packer`. You'll have to create that
- Once you create the new key, put the contents of `/.ssh/packer.pub` into
  `user-data` where the existing public key is.

Someday I'll automate this.

## Building an image

Just run:

```
make
```

This will download the base image, set it up, and eventually output it in
`packer-out`.

The `qemu.sh` helper will let you boot the image.

## Default credentials & regenerating them

If you need to troubleshoot anything by logging in on the console, the
credentials are:

Username: `packer`
Password: `cloud123`

You can change them by editing `user-data`. This is how I regenerate the
password hash:

```
openssl passwd -1 -salt $(dd if=/dev/urandom bs=6 count=1 status=none | base64)
```
