"""
A helper for creating cloudinit VMs. We use LVM storage, so we expect
an LVM volume group to be set up for our use.

Sample usage:
$ cloudinit-lvm.py create [--name node0] [more optional flags]
$ cloudinit-lvm.py list
$ cloudinit-lvm.py delete --name cloudinit_node0

'create' takes a lot of flags. See --help for options.

Some notes on dependencies:
- This script expects a working `virsh`, `virt-install`, and `qemu-img`.
- A config file, by default cloudinit-lvm.yaml in your current directory. It
  must specify install_image_dir (where your base images live) and disk_pool (where
  your live VM images live) at the top -- you'll want to set those appropriately.
"""

import os
import os.path
import pwd
import subprocess
import sys
import random
import typing
import xml.etree.ElementTree as ET

import yaml
from absl import app
from absl import flags
from absl import logging

flags.DEFINE_string(
    'name', None,
    'Name of VM. If this is None, we will auto-generate a random one.')
flags.DEFINE_string(
    'image', 'debian-11.img',
    'Disk image to use. You can set the default in the config.')
flags.DEFINE_integer('ram_mb', 1024, 'RAM for VM, in MB')
flags.DEFINE_integer('cpus', 1, 'CPUs for VM')
flags.DEFINE_string('network', 'virbr0', 'libvirt network to attach VM to')
flags.DEFINE_string('os_variant', 'debian7',
                    'OS variant to pass to virt-install')
flags.DEFINE_string('disk_size', '25G',
                    'Size of main disk of VM; can use M, G, etc, suffix')
flags.DEFINE_string(
    'data_disk_size', '0',
    'Size of data disk of VM, if not "0"; can use M, G, etc, suffix')
flags.DEFINE_string('data_disk_fs', 'ext4', 'Filesystem to use on data disk.')
flags.DEFINE_string('user', 'cloud', 'User to create')
flags.DEFINE_string(
    'keyfile', None,
    'Where to find ssh keys for user. If this is None, we will do our best to'
    'find your authorized_keys file.')
flags.DEFINE_boolean(
    'password', False,
    'If true, set a password for this user. Otherwise, lock the password.')
flags.DEFINE_string(
    'pass_hash',
    '$6$saltsalt$wVzOxp139jXJm2bHzpMAu/52NJLuaPceqzdvGa./Pxu5.amCga/iJsPLejmOHcd6/EAsslzKy79a49nP85FMR0',
    'Hash of password for user; ONLY USED IF YOU ALSO PASS --password. Default is the hash of "cloud123"'
)
flags.DEFINE_boolean(
    'dhcp', True,
    'If true, use DHCP. Otherwise, use the other --net-* options.')
flags.DEFINE_string(
    'net_device', None,
    'Device name to apply network settings to. This must match one of the devices that already exists on the device. (This does not create a new device.)'
)
flags.DEFINE_string('net_address', None,
                    'If set, IP of VM. Used if --dhcp=false.')
flags.DEFINE_string('net_nameservers', None,
                    'If set, DNS server for VM. Used if --dhcp=false.')
flags.DEFINE_string('net_gateway', None,
                    'If set, gateway for VM. Used if --dhcp=false.')
flags.DEFINE_string('net_domain', None,
                    'If set, DNS search domain for VM. Used if --dhcp=false.')
flags.DEFINE_string('net_netmask', None,
                    'If set, netmask for VM. Used if --dhcp=false.')
flags.DEFINE_string('config', './cloudinit-lvm.yaml',
                    'Config file to read settings from')
flags.DEFINE_string('post_create', '',
                    'Shell commands to run after creating a VM.')
flags.DEFINE_string('post_delete', '',
                    'Shell commands to run after deleting a VM.')
flags.DEFINE_string(
    'prefix', 'cloudinit_',
    'Prefix we add to all VM names and LVM LVs. We do this to try to '
    'namespace our data as much as possible. BE CAREFUL if you'
    'set this to the empty string.')
flags.DEFINE_boolean('clean_up', True, 'Clean up temp files')
flags.DEFINE_boolean('dry_run', False, 'Do not run destructive shell commands')


class Config(typing.NamedTuple):
    """Typed global configuration."""
    install_image_dir: str
    disk_pool: str
    data_disk_pool: str
    defaults: typing.Optional[typing.Dict[str, typing.Union[str, int, bool]]]

    @staticmethod
    def load(filename):
        with open(filename, 'r') as fh:
            data = yaml.safe_load(fh)
            c = data['config']
            defaults = data.get('defaults', {})
        cfg = Config(
            install_image_dir=c['install_image_dir'],
            disk_pool=c['disk_pool'],
            data_disk_pool=c['data_disk_pool'],
            defaults=defaults,
        )
        logging.debug(f"Loaded config from {filename}: {cfg}")
        return cfg

    def apply_defaults(self, global_flags):
        # To apply defaults, we re-parse argv with defaults from the config first.
        cmdline_with_defaults = (
            [sys.argv[0]] + list(flags.flag_dict_to_args(CONFIG.defaults)) +
            sys.argv[1:])
        logging.debug(f"Commandline with defaults: {cmdline_with_defaults}")
        return global_flags(cmdline_with_defaults)


FLAGS = flags.FLAGS
CONFIG = None
METADATA_FILE = "meta-data"
USERDATA_FILE = "user-data"

# We show this to the user when creating or deleting hosts without a prefix.
BIG_SCARY_WARNING = """

*** WARNING ***
You're running with --prefix='', which means this script will try to
create/delete LVMs with any name you give it. Carefully look over the names of
the VMs and LVs you'll be affecting!

(You will be prompted again before any changes are made.)
"""


def run(args, run_even_if_dry_run=False):
    """Runs a shell command, discarding output.

    We don't run if dry_run is true, unless run_even_if_dry_run is true.
    """
    if FLAGS.dry_run and not run_even_if_dry_run:
        logging.info(f"Would run: {args}")
        return
    logging.debug(f"Running: {args}")
    return subprocess.run(args, check=True)


def out(args, run_even_if_dry_run=False):
    """Runs a shell command, storing output.

    We don't run if dry_run is true, unless run_even_if_dry_run is true.
    """
    if FLAGS.dry_run and not run_even_if_dry_run:
        logging.info(f"Would run: {args}")
        return ''
    logging.debug(f"Running: {args}")
    return subprocess.check_output(args).decode('utf-8').rstrip("\n")


def err_quit(*args):
    """Logs an error message and quits."""
    logging.error(*args)
    exit(1)


def confirm(msg="OK?"):
    """Asks the user for confirmation."""
    dry_run_str = "[DRY RUN] " if FLAGS.dry_run else ""
    print(f'{dry_run_str}{msg} [y/N] ', end='', flush=True)
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


def _get_ssh_keys():
    if FLAGS.keyfile is None:
        user = os.getenv('SUDO_USER', os.getenv('USER'))
        home = pwd.getpwnam(user).pw_dir
        keyfile = f"{home}/.ssh/authorized_keys"
    else:
        keyfile = FLAGS.keyfile
    logging.debug(f"Looking for ssh keys in: {keyfile}")

    keys = []
    with open(keyfile, 'r') as fh:
        for line in fh.readlines():
            if line.strip().startswith('#') or not line:
                continue
            keys.append(line.strip())

    logging.info(f"Found {len(keys)} keys in {keyfile}.")
    return keys


def _random_hostname():
    chars = list("abcdefghijklmnopqrstuvwxyz")
    r = random.SystemRandom()
    return ''.join([r.choice(chars) for _ in range(6)])


def _get_device_path(pool, vol):
    if FLAGS.dry_run:
        return f"<dry run, path TBD: pool={pool}, vol={vol}>"
    xml_str = out(['virsh', 'vol-dumpxml', '--pool', pool, vol])
    xml_root = ET.fromstring(xml_str)
    dev = xml_root.find('./target/path')
    return dev.text


def do_create():
    if FLAGS.prefix == "":
        print(BIG_SCARY_WARNING)
        if not confirm("Are you being careful?"):
            return
    if FLAGS.name is None:
        name = _random_hostname()
        logging.debug(f'Auto-generating name {name}')
    else:
        name = FLAGS.name
    if FLAGS.dry_run:
        logging.info("DRY-RUN create")

    prefix = FLAGS.prefix
    install_image_dir = CONFIG.install_image_dir
    disk_pool = CONFIG.disk_pool
    data_disk_pool = CONFIG.data_disk_pool

    logging.info(f"CREATE {name}")
    domain = out(["hostname", "-d"], run_even_if_dry_run=True)

    disk = prefix + name
    data_disk = f"{prefix}{name}_data"

    disk_base = f"{install_image_dir}/{FLAGS.image}"
    ssh_keys = _get_ssh_keys()
    lock_passwd = not FLAGS.password
    pass_hash = FLAGS.pass_hash if FLAGS.password else '!!'

    # TODO: Lots of this could come from the config file. We could even insert
    # whole pieces of our config directly into the user-data.
    userdata_dict = {
        "preserve_hostname":
        False,
        "fqdn":
        f"{name}.{domain}",
        "users": [
            {
                "name": FLAGS.user,
                "shell": "/bin/bash",
                "sudo": ["ALL=(ALL) NOPASSWD:ALL"],
                "lock_passwd": lock_passwd,
                "passwd": pass_hash,
                "ssh_authorized_keys": ssh_keys,
            },
        ],
        "runcmd": [
            "touch /etc/cloud/cloud-init.disabled",
            "poweroff",
        ],
    }
    if FLAGS.data_disk_size != "0":
        userdata_dict["mounts"] = [[
            "vdb", "/data", "auto", "defaults,nofail", "0", "0"
        ]]
        userdata_dict["fs_setup"] = [
            {
                "label": "data",
                "device": "/dev/vdb",
                "filesystem": FLAGS.data_disk_fs,
                "partition": "auto"
            },
        ]

    metadata_dict = {"instance-id": prefix + name, "local-hostname": name}
    if not FLAGS.dhcp:
        metadata_dict["network-interfaces"] = "\n".join([
            f"auto lo",
            f"iface lo inet loopback",
            "",
            f"auto {FLAGS.net_device}",
            f"iface {FLAGS.net_device} inet static",
            f"address {FLAGS.net_address}",
            f"netmask {FLAGS.net_netmask}",
            f"gateway {FLAGS.net_gateway}",
            "",
            f"dns-domain {FLAGS.net_domain}",
            f"dns-nameservers {FLAGS.net_nameservers}",
        ])

    userdata = "#cloud-config\n" + yaml.dump(userdata_dict)
    metadata = yaml.dump(metadata_dict)

    print("===================\n"
          f"Node name: {name}.{domain}\n"
          f"User name: {FLAGS.user}\n"
          "===================\n"
          f"RAM: {FLAGS.ram_mb} MB\n"
          f"CPUs: {FLAGS.cpus}\n"
          f"Cloudinit image: {disk_base}\n"
          f"Root disk size: {FLAGS.disk_size} on vol={disk_pool}/{disk}")
    if FLAGS.data_disk_size != "0":
        print(
            f"Data Disk size: {FLAGS.data_disk_size} on vol={data_disk_pool}/{data_disk})"
        )
    print()

    print(f"User-data:\n{userdata}")
    print(f"Meta-data:\n{metadata}")

    post_create_cmd = _make_post_create_cmd({
        "name": name,
        "full_name": prefix + name,
        "disk": disk,
        "disk_pool": disk_pool,
        "disk_size": FLAGS.disk_size,
        "data_disk": data_disk,
        "data_disk_pool": data_disk_pool,
        "data_disk_size": FLAGS.data_disk_size,
        "domain": domain,
        "ssh_keys": ssh_keys,
        "net_device": FLAGS.net_device,
        "net_address": FLAGS.net_address,
        "net_gateway": FLAGS.net_gateway,
        "net_nameservers": FLAGS.net_nameservers,
        "net_netmask": FLAGS.net_netmask,
        "net_domain": FLAGS.net_domain,
    })
    print(f"Post create command: {post_create_cmd}")

    if not os.path.exists(disk_base):
        logging.error(f"Disk image {disk_base} does not exist!")
        if not FLAGS.dry_run:
            return

    if not confirm(f"Create VM {name}?"):
        print('Cancelled.')
        return

    # We expect the cloud image to automatically resize to the size of its disk
    # on first boot.
    data_disk_args = []
    run([
        'virsh', 'vol-create-as', '--pool', disk_pool, '--format', 'raw',
        '--name', disk, '--allocation', FLAGS.disk_size, '--capacity',
        FLAGS.disk_size
    ])
    disk_dev = _get_device_path(disk_pool, disk)

    if FLAGS.data_disk_size != "0":
        run([
            'virsh', 'vol-create-as', '--pool', data_disk_pool, '--format',
            'raw', '--name', data_disk, '--allocation', FLAGS.data_disk_size,
            '--capacity', FLAGS.data_disk_size
        ])
        data_disk_args.append(f"--disk=vol={data_disk_pool}/{data_disk}")
        data_disk_dev = _get_device_path(data_disk_pool, data_disk)

    # populate new devices
    logging.info(f"Copying {disk_base} to {disk_dev}...")
    run([
        "qemu-img",
        "convert",
        "-n",  # do not resize the image (relevant if output is a file)
        "-p",  # show progress
        "-O",  # convert to a raw disk image, not a sparse format
        "raw",
        disk_base,
        disk_dev,
    ])
    with open(METADATA_FILE, 'w') as fh:
        fh.write(metadata)
    with open(USERDATA_FILE, 'w') as fh:
        fh.write(userdata)

    run([
        "virt-install", "--import", f"--name={prefix}{name}",
        f"--os-variant={FLAGS.os_variant}", f"--ram={FLAGS.ram_mb}",
        f"--vcpus={FLAGS.cpus}", f"--disk=vol={disk_pool}/{disk}",
        f"--cloud-init=user-data={USERDATA_FILE},meta-data={METADATA_FILE}"
    ] + data_disk_args + [
        f"--network=bridge={FLAGS.network}",
        "--autostart",
        "--noautoconsole",
        "--graphics=vnc",
        "--wait=3",
    ])

    logging.info(f"VM {prefix}{name} was created.")
    print("To connect to the console, run:\n"
          f"  virsh console {prefix}{name}")
    run(["sh", "-c", post_create_cmd])


def do_delete():
    if FLAGS.prefix == "":
        print(BIG_SCARY_WARNING)
        if not confirm("Are you being careful?"):
            return
    if FLAGS.name is None:
        err_quit("--name is required with --delete")
    if FLAGS.dry_run:
        logging.info("DRY-RUN delete")
    prefix = FLAGS.prefix
    dom = FLAGS.name

    logging.info(f"Deleting {dom}")

    if not dom.startswith(prefix):
        err_quit(f"{dom} does not start with prefix {prefix}. We will not"
                 "delete VMs we did not create!")

    if dom not in _list_vms(True):
        err_quit(f"VM {dom} does not exist")

    all_devices = _list_devices(dom)
    print("*** We will permanently delete the following disks ***")
    run(["virsh", "domblklist", dom], run_even_if_dry_run=True)
    post_delete_cmd = _make_post_delete_cmd({
        "name": dom[len(prefix):],
        "full_name": dom,
        "devices": " ".join(all_devices),
    })
    print(f"Post delete command: {post_delete_cmd}")

    if not confirm(f"Permanently VM {dom} and its associated disks?"):
        print('Cancelled.')
        return

    run(["virsh", "destroy", dom])
    for dev in all_devices:
        _wipe_dev(dev)
    run(["virsh", "undefine", "--remove-all-storage", dom])

    logging.info(f"VM {dom} was removed.")
    run(["sh", "-c", post_delete_cmd])


def _detach_disk(dom, dev):
    run([
        "virsh", "detach-disk", "--config", "--persistent", FLAGS.prefix + dom,
        dev
    ])


def _wipe_dev(dev):
    run(["wipefs", "--all", dev])


def _start_dom(dom):
    run(["virsh", "start", FLAGS.prefix + dom])


def _list_devices(dom):
    lines = out(["virsh", "domblklist", dom], run_even_if_dry_run=True)
    devs = []
    for line in lines.split('\n')[2:]:
        parts = line.strip().split()
        if parts[1].startswith('/dev/'):
            devs.append(parts[1])
    return devs


def _list_vms(list_all):
    maybe_all = ["--all"] if list_all else []
    names = out(["virsh", "list", "--name"] + maybe_all,
                run_even_if_dry_run=True)
    return [n for n in names.split('\n') if n.startswith(FLAGS.prefix)]


def _make_post_create_cmd(args):
    logging.debug(f"Post create actions: {FLAGS.post_create}")
    cmd = FLAGS.post_create.format(**args)
    logging.debug(f"Post create command: {cmd}")
    return cmd


def _make_post_delete_cmd(args):
    logging.debug(f"Post delete actions: {FLAGS.post_delete}")
    cmd = FLAGS.post_delete.format(**args)
    logging.debug(f"Post delete command: {cmd}")
    return cmd


def do_list():
    for vm in _list_vms(False):
        print(vm)


def main(argv):
    global CONFIG

    known_ops = {"create", "delete", "list"}
    if len(argv) != 2:
        err_quit(f"Exactly one operation is required: {known_ops}")
    op = argv[1]
    if op not in {"create", "delete", "list"}:
        err_quit(f"Unknown operation {op} -- expecting one of: {known_ops}")

    logging.info(FLAGS["name"].value)
    CONFIG = Config.load(FLAGS.config)
    args = CONFIG.apply_defaults(FLAGS)
    if op == "create":
        try:
            do_create()
        finally:
            if FLAGS.clean_up:
                _clean_up()
    elif op == "delete":
        do_delete()
    elif op == "list":
        do_list()


if __name__ == '__main__':
    app.run(main)
