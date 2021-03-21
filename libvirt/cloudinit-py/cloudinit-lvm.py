#!/usr/bin/python3
"""
A helper for creating cloudinit VMs. We use LVM storage, so we expect
$disk_vg (below) to exist and be a recognized storage pool.

Sample usage:
$ cloudinit-lvm.py --create --name node0
$ cloudinit-lvm.py --list
$ cloudinit-lvm.py --delete --name node0

See --help for options.

Some notes on dependencies:
- This script expects a working `virsh` and `virt-install`
- This script disk_base_dir (where your base images live) and disk_vg (where
  your live VM images live) at the top -- you'll want to set those appropriately.
"""

import os
import os.path
import pwd
import subprocess
import sys
import uuid

from absl import app
from absl import flags
from absl import logging

## === Globals ===
## Base images -- these are different than the images we download from the
## internet. There is a conversion step:
## qemu-img convert vmachine.qcow2 -O raw vmachine.raw
## See https://manurevah.com/blah/en/p/Convert-qcow2-to-LVM for more info.
disk_base_dir = "/data/cloud-init-kvm"
## Live VM images
disk_vg = "libvirt_lvm"
## VG to create data disks on. This can be the same as disk_vg, above, or it can
## be different.
data_disk_vg = "libvirt_lvm_slow"

METADATA_FILE = "meta-data"
USERDATA_FILE = "user-data"

## We add this prefix to all LVM disk names, so this script operates in its own
## world, even if it shares a VG with other VMs. (Even if you try to delete a VM
## this script didn't create, we'll only ever try to delete things beginning with
## this prefix.) If you want to create a long-lived VM that you don't want to
## share this prefix, you can set this to "", but don't mess around with this
## blank.
prefix = "cloudinit_"

FLAGS = flags.FLAGS

flags.DEFINE_boolean('create', False, 'Create a VM')
flags.DEFINE_boolean('delete', False, 'Delete a VM')
flags.DEFINE_boolean('list', False, 'List VMs')
flags.DEFINE_string('name', None, 'Name of VM')
flags.DEFINE_string('image', 'ubuntu-19.04.raw', 'Disk image to use')
flags.DEFINE_integer('ram_mb', 1024, 'RAM for VM, in MB')
flags.DEFINE_integer('cpus', 1, 'CPUs for VM')
flags.DEFINE_string('disk_size', '25G',
                    'Size of main disk of VM; can use M, G, etc, suffix')
flags.DEFINE_string(
    'data_disk_size', '0',
    'Size of data disk of VM, if not "0"; can use M, G, etc, suffix')
flags.DEFINE_string('user', 'cloud', 'User to create')
flags.DEFINE_string(
    'pass_hash',
    '$6$saltsalt$wVzOxp139jXJm2bHzpMAu/52NJLuaPceqzdvGa./Pxu5.amCga/iJsPLejmOHcd6/EAsslzKy79a49nP85FMR0',
    'Hash of password for user; default is the hash of "cloud123"')
flags.DEFINE_boolean('clean_up', False, 'Cleanup temp files')
flags.DEFINE_boolean('dry_run', False, 'Do not run shell commands')


def run(args, run_even_if_dry_run=False):
    if FLAGS.dry_run and not run_even_if_dry_run:
        logging.info(f"Would run: {args}")
        return
    logging.debug(f"Running: {args}")
    return subprocess.run(args, check=True)


def out(args, run_even_if_dry_run=False):
    if FLAGS.dry_run and not run_even_if_dry_run:
        logging.info(f"Would run: {args}")
        return ''
    logging.debug(f"Running: {args}")
    return subprocess.check_output(args).decode('utf-8').rstrip("\n")


def err_quit(*args):
    logging.error(*args)
    exit(1)


def confirm(msg="OK?"):
    print(f'{msg} [y/N] ', end='', flush=True)
    resp = sys.stdin.readline()
    return resp.strip().lower() in ["y", "yes"]


def _clean_up():
    files = [METADATA_FILE, USERDATA_FILE]
    if FLAGS.dry_run:
        logging.debug("Skipping cleanup because of dry-run")
        return
    logging.debug(f"Cleaning up: {files}")
    try:
        for f in files:
            os.unlink(f)
    except FileNotFoundError:
        pass


def _get_ssh_key():
    user = os.getenv('SUDO_USER', os.getenv('USER'))
    home = pwd.getpwnam(user).pw_dir
    keyfile = f"{home}/.ssh/authorized_keys"
    logging.info(f"Looking for ssh keys in: {keyfile}")

    key = None
    warn = False
    with open(keyfile, 'r') as fh:
        for line in fh.readlines():
            if not line.strip().startswith('#'):
                if key is None:
                    key = line
                else:
                    # We have more than one key; warn the user we're picking
                    # just one.
                    warn = True

    if warn:
        logging.warning(
            f'{keyfile} contains more than one key, we will use only the first'
        )
    return key


def do_create():
    if FLAGS.name is None:
        FLAGS.name = str(uuid.uuid1())[:8]
        logging.info(f'Auto-generating name {FLAGS.name}')

    logging.info(f"CREATE {FLAGS.name}")
    name = FLAGS.name
    fqdn = out(["hostname", "-d"], run_even_if_dry_run=True)

    disk = prefix + name
    data_disk = f"{prefix}{name}_data"
    cidata = f"{prefix}{name}_cidata"

    disk_dev = f"/dev/{disk_vg}/{disk}"
    data_disk_dev = f"/dev/{data_disk_vg}/{data_disk}"
    cidata_dev = f"/dev/{disk_vg}/{cidata}"

    disk_base = f"{disk_base_dir}/{FLAGS.image}"
    ssh_key = _get_ssh_key()
    userdata = f"""#cloud-config
preserve_hostname: False
hostname: {name}
fqdn: '{fqdn}'
users:
  - name: {FLAGS.user}
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    lock_passwd: false
    passwd: '{FLAGS.pass_hash}'
    ssh_authorized_keys:
      - '{ssh_key}'
runcmd:
  - ['systemctl', 'restart', 'networking']
"""

    print("===================\n"
          f"Node name: {name} ({fqdn})\n"
          f"User name: {FLAGS.user}\n"
          "===================\n")
    print(f"RAM: {FLAGS.ram_mb} MB\n"
          f"CPUs: {FLAGS.cpus}\n"
          f"Disk base: {disk_base}\n"
          f"Root disk size: {FLAGS.disk_size} (on {disk_dev})\n")
    if FLAGS.data_disk_size != "0":
        print(f"Data Disk size: {FLAGS.data_disk_size} (on {data_disk_dev})")
    print(f"User-data:\n{userdata}")

    if not os.path.exists(disk_base):
        logging.error(f"Disk image {disk_base} does not exist!")
        if not FLAGS.dry_run:
            return

    if not confirm():
        print('Cancelled.')
        return

    # We only pass disk size to LVM, because we expect the cloud image to
    # automatically resize to the size of its disk on first boot.
    run([
        "lvcreate", "--yes", "--size", FLAGS.disk_size, "--name", disk, disk_vg
    ])
    run(["lvcreate", "--yes", "--size", "4M", "--name", cidata, disk_vg])
    data_disk_args = []
    if FLAGS.data_disk_size != "0":
        run([
            "lvcreate", "--yes", "y", "--size", FLAGS.data_disk_size, "--name",
            data_disk, data_disk_vg
        ])
        data_disk_args.append(f"--disk={data_disk_dev}")

    # populate new devices
    print(f"Copying {disk_base} to {disk_dev}...")
    run([
        "dd", "status=progress", "bs=2048", f"if={disk_base}", f"of={disk_dev}"
    ])
    with open(METADATA_FILE, 'w') as fh:
        fh.write(f"instance-id: {prefix}{name}\nlocal-hostname: {fqdn}\n")
    with open(USERDATA_FILE, 'w') as fh:
        fh.write(userdata)

    run([
        "genisoimage", "-output", cidata_dev, "-volid", "cidata", "-joliet",
        "-rock", "user-data", "meta-data"
    ])

    run([
        "virt-install", "--import", f"--name={prefix}{name}",
        "--os-variant=debian7", f"--ram={FLAGS.ram_mb}",
        f"--vcpus={FLAGS.cpus}", f"--disk={disk_dev}"
    ] + data_disk_args + [
        f"--disk={cidata_dev},device=cdrom", "--network=bridge=virbr0",
        "--noautoconsole", "--graphics=vnc"
    ])

    print("To connect to the console, run:\n"
          f"  virsh console {prefix}{name}")


def do_delete():
    if FLAGS.name is None:
        err_quit("--name is required with --delete")
    logging.info(f"Deleting {FLAGS.name}")
    name = FLAGS.name
    dom = prefix + name

    if dom not in _list_vms():
        # TODO: support deleting stopped VMs
        err_quit(f"{dom} is not a running VM")

    disk = prefix + name
    data_disk = f"{prefix}{name}_data"
    cidata = f"{prefix}{name}_cidata"

    data_disk_dev = f"/dev/{data_disk_vg}/{data_disk}"

    print("Root disk:")
    run(["lvdisplay", f"{disk_vg}/{disk}"])

    delete_data_disk = False
    if os.path.exists(data_disk_dev):
        delete_data_disk = True
        print("Data disk:")
        run(["lvdisplay", f"{disk_vg}/{data_disk}"])

    if not confirm():
        print('Cancelled.')
        return

    run(["virsh", "destroy", dom])
    run(["virsh", "undefine", dom])
    run(["lvremove", "--yes", f"{disk_vg}/{cidata}"])
    if delete_data_disk:
        run(["lvremove", "--yes", f"{disk_vg}/{data_disk}"])
    run(["lvremove", "--yes", f"{disk_vg}/{disk}"])


def _list_vms():
    names = out(["sudo", "virsh", "list", "--name"], run_even_if_dry_run=True)
    return [n for n in names.split('\n') if n.startswith(prefix)]


def do_list():
    for vm in _list_vms():
        print(vm)


def main(argv):
    op_args = [FLAGS.create, FLAGS.delete, FLAGS.list]
    if sum(op_args) != 1:
        err_quit("Exactly one operation flag is required: "
                 "--create, --delete, --list")
    if FLAGS.create:
        try:
            do_create()
        finally:
            if FLAGS.clean_up:
                _clean_up()
    elif FLAGS.delete:
        do_delete()
    elif FLAGS.list:
        do_list()


if __name__ == '__main__':
    app.run(main)
