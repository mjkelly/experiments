#!/bin/bash
# A helper for creating cloudinit VMs. We use LVM storage, so we expect
# $disk_vg (below) to exist and be a recognized storage pool.
#
# Sample usage:
# $ cloudinit.sh --create --name node0
# $ cloudinit.sh --list
# $ cloudinit.sh --delete --name node0
#
# See --help for options.
#
# Some notes on dependencies:
# - This script expects a working `virsh` and `virt-install`
# - This script disk_base_dir (where your base images live) and disk_vg (where
#   your live VM images live) at the top -- you'll want to set those appropriately.

set -e
set -u

# === Globals ===
# Base images -- these are different than the images we download from the
# internet. There is a conversion step:
# qemu-img convert vmachine.qcow2 -O raw vmachine.raw
# See https://manurevah.com/blah/en/p/Convert-qcow2-to-LVM for more info.
disk_base_dir=/data/cloud-init-kvm
# Live VM images
disk_vg=libvirt_lvm
# VG to create data disks on. This can be the same as disk_vg, above, or it can
# be different.
data_disk_vg=libvirt_lvm_slow


# === Default values for flags ===
name=''
op=''
#image=debian-9.5.6-20181013-openstack-arm64.qcow2
image=ubuntu-19.04.raw
ram_mb=1024
cpus=1
disk_size=25G
data_disk_size=0
user=cloud
# This is just cloud123 :)
pass_hash='$6$saltsalt$wVzOxp139jXJm2bHzpMAu/52NJLuaPceqzdvGa./Pxu5.amCga/iJsPLejmOHcd6/EAsslzKy79a49nP85FMR0'
if [[ -n $SUDO_USER ]]; then
  # if we were invoked via sudo, we almost certainly want $SUDO_USER's
  # authorized_keys.
  keys_file="$(getent passwd $SUDO_USER | cut -d: -f6)/.ssh/authorized_keys"
else
  keys_file=$HOME/.ssh/authorized_keys
fi

# === Flag parsing ===
opts=$(getopt \
  --longoptions create,delete,list,help,name:,image:,ram_mb:,cpus:,disk-size:,data-disk-size:,keys_file:,user:,pass_hash: \
  --name "$(basename $0)" \
  --options "" \
  -- "$@")
eval set -- $opts

while [[ $# -gt 0 ]]; do
  case "$1" in
    # Operations
    --create)
      op=create
      shift;;
    --delete)
      op=delete
      shift;;
    --list)
      op=list
      shift;;
    --help)
      op=help
      shift;;
    # Flags
    --name)
      name=$2
      shift 2;;
    --image)
      image=$2
      shift 2;;
    --ram_mb)
      ram_mb=$2
      shift 2;;
    --cpus)
      cpus=$2
      shift 2;;
    --disk-size)
      disk_size=$2
      shift 2;;
    --data-disk-size)
      data_disk_size=$2
      shift 2;;
    --keys_file)
      keys_file=$2
      shift 2;;
    --user)
      user=$2
      shift 2;;
    --pass_hash)
      pass_hash=$2
      shift 2;;
    *)
      break;;
  esac
done

# === Function definitions ===

function create_vm() {
  if [[ $name == '' ]]; then
    name="$(uuidgen -r | cut -c 1-8)"
  fi
  # These are always derived from $name
  disk="cloudinit-${name}"
  data_disk="cloudinit-${name}-data"
  cidata="cloudinit-${name}-cidata"

  disk_dev="/dev/${disk_vg}/${disk}"
  data_disk_dev="/dev/${data_disk_vg}/${data_disk}"
  cidata_dev="/dev/${disk_vg}/${cidata}"


  disk_base="${disk_base_dir}/${image}"
  ssh_key="$(cat "$keys_file")"
  domain="$(hostname -d)"
  fqdn="${name}.${domain}"

  ls -l "${disk_base}"

  cat <<_EOF_ > user-data
#cloud-config
preserve_hostname: False
hostname: ${name}
fqdn: ${fqdn}
users:
  - name: ${user}
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    lock_passwd: false
    passwd: '${pass_hash}'
    ssh_authorized_keys:
      - '${ssh_key}'
runcmd:
  - ['systemctl', 'restart', 'networking']
_EOF_

  echo "==================="
  echo "Node name: ${name} ($fqdn)"
  echo "User name: ${user}"
  echo "==================="
  echo "RAM: $ram_mb MB"
  echo "CPUs: $cpus"
  echo "Disk base: ${disk_base}"
  echo "Root disk size: ${disk_size} (on ${disk_dev})"
  if [[ $data_disk_size != "0" ]]; then
    echo "Data Disk size: ${data_disk_size} (on ${data_disk_dev})"
  fi
  echo "User-data:"
  cat user-data

  echo
  echo -n "OK? [y/N] "
  read yesno

  if [[ $yesno != "y" && $yesno != "yes" ]]; then
    echo "Cancelled."
    exit 1
  fi
   
  # We only pass disk size to LVM, because we expect the cloud image to
  # automatically resize to the size of its disk on first boot.
  lvcreate --size ${disk_size} --name ${disk} ${disk_vg}
  lvcreate --size 4M --name ${cidata} ${disk_vg}
  if [[ $data_disk_size != "0" ]]; then
    lvcreate --size ${data_disk_size} --name ${data_disk} ${data_disk_vg}
    data_disk_arg="--disk=${data_disk_dev}"
  else
    data_disk_arg=''
  fi

  # populate new devices
  echo "Copying ${disk_base} to ${disk_dev}..."
  dd bs=2048 if=${disk_base} of=${disk_dev}
  echo -e "instance-id: cloudinit-$name\nlocal-hostname: $fqdn\n" > meta-data
  genisoimage -output ${cidata_dev} -volid cidata -joliet -rock user-data meta-data
  virt-install \
    --import \
    --name=cloudinit-$name \
    --os-variant=debian7 \
    --ram=${ram_mb} \
    --vcpus=${cpus} \
    --disk=${disk_dev} \
    ${data_disk_arg} \
    --disk=${cidata_dev},device=cdrom \
    --network=bridge=virbr0 \
    --noautoconsole \
    --graphics=vnc

  echo "To connect to the console, run:"
  echo "  virsh console cloudinit-${name}"
}

function delete_vm() {
  if [[ $name == '' ]]; then
    echo "--name is required"
    exit 2
  fi
  # These are always derived from $name
  disk="cloudinit-${name}"
  data_disk="cloudinit-${name}-data"
  cidata="cloudinit-${name}-cidata"

  disk_dev="/dev/${disk_vg}/${disk}"
  data_disk_dev="/dev/${data_disk_vg}/${data_disk}"
  cidata_dev="/dev/${disk_vg}/${cidata}"

  # Since we don't have our own metadata, we can either try to inspect the
  # domain config, or just check for the data disk device. We check for the
  # device.
  if [[ ! -e "${data_disk_dev}" ]]; then
    data_disk=""
    data_disk_dev=""
  fi

  local dom=cloudinit-$name
  echo "Will remove node: $dom"
  echo "Root disk image:"
  lvdisplay "${disk_vg}/${disk}"
  if [[ -n $data_disk ]]; then
    echo "Data disk image:"
    lvdisplay "${data_disk_vg}/${data_disk}"
  fi

  echo -n "OK? [y/N] "
  read yesno
  if [[ $yesno != "y" && $yesno != "yes" ]]; then
    echo "Cancelled."
    exit 1
  fi

  virsh destroy $dom
  virsh undefine $dom
  lvremove "${disk_vg}/${disk}"
  if [[ -n $data_disk ]]; then
    lvremove "${data_disk_vg}/${data_disk}"
  fi
  lvremove "${disk_vg}/${cidata}"

}

function list_vms() {
  sudo virsh list --name | grep ^cloudinit- | sed 's/^cloudinit-//'
}

function help_and_exit() {
  echo "Usage:"
  echo "  $0 --create [options]"
  echo "  $0 --list [options]"
  echo "  $0 --delete --name <name> [options]"
  echo "Options:"
  echo "  --name <vm_name>"
  echo "  --image <disk image>"
  echo "    Name of file in ${disk_base_dir}"
  echo "  --ram_mb <vm_ram_in_mb>"
  echo "  --cpus <cpu_count>"
  echo "  --disk-size <disk size>"
  echo "    Size of the root disk. We accept any format understood by LVM:"
  echo "    e.g., 'M' and 'G' suffixes."
  echo "  --data-disk-size <disk size>"
  echo "    Size of an additional data disk. Same format as --disk-size."
  echo "    (We don't automatically mount this.)"
  echo "  --keys_file <authorized_keys_file>"
  echo "  --user <default user>"
  echo "  --pass_hash <user_password_hash>"
  echo
  echo "Available disk images:"
  ls -1 ${disk_base_dir}
  exit 1
}

# === main ===
if [[ $op == create ]]; then
  create_vm
elif [[ $op == delete ]]; then
  delete_vm
elif [[ $op == list ]]; then
  list_vms
elif [[ $op == help ]]; then
  help_and_exit
else
  echo "Either --create, --delete, or --list is required"
  exit 2
fi
