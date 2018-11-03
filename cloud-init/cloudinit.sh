#!/bin/bash
# A helper for creating cloudinit VMs.
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
# - This script disk_base_dir (where your base images live) and disk_dir (where
#   your live VM images live) at the top -- you'll want to set those appropriately.

set -e
set -u

# === Globals ===
# Base images
disk_base_dir=/var/lib/virt/cloud-init/disks
# Live VM images
disk_dir=/var/lib/virt/cloud-init


# === Default values for flags ===
name=''
op=''
#image=debian-9.5.6-20181013-openstack-arm64.qcow2
image=xenial-server-cloudimg-amd64-disk1.img
ram_mb=1024
cpus=1
keys_file=$HOME/.ssh/authorized_keys
user=cloud
# This is just cloud123 :)
pass_hash='$6$saltsalt$wVzOxp139jXJm2bHzpMAu/52NJLuaPceqzdvGa./Pxu5.amCga/iJsPLejmOHcd6/EAsslzKy79a49nP85FMR0'

# === Flag parsing ===
opts=$(getopt \
  --longoptions create,delete,list,help,name:,image:,ram_mb:,cpus:,keys_file:,user:,pass_hash: \
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
  disk="${disk_dir}/${name}.raw"
  cidata="${disk_dir}/${name}-cidata.iso"

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
    passwd: ${pass_hash}
    ssh_authorized_keys:
      - ${ssh_key}
runcmd:
  - [systemctl, restart, networking]
_EOF_

  echo "==================="
  echo "Node name: ${name} ($fqdn)"
  echo "User name: ${user}"
  echo "==================="
  echo "RAM: $ram_mb MB"
  echo "CPUs: $cpus"
  echo "Disk base: ${disk_base}"
  echo "Live VM disk image: ${disk}"
  echo "User-data:"
  cat user-data

  echo
  echo -n "OK? [y/N] "
  read yesno

  if [[ $yesno != "y" && $yesno != "yes" ]]; then
    echo "Cancelled."
    exit 1
  fi
   
  cp "${disk_base}" "${disk}"
  echo -e "instance-id: cloudinit-$name\nlocal-hostname: $fqdn\n" > meta-data
  genisoimage -output ${cidata} -volid cidata -joliet -rock user-data meta-data
  virt-install \
    --import \
    --name cloudinit-$name \
    --os-variant debian7 \
    --ram ${ram_mb} \
    --vcpus ${cpus} \
    --disk ${disk} \
    --disk ${cidata},device=cdrom \
    --network bridge=virbr0 \
    --noautoconsole \
    --graphics vnc
}

function delete_vm() {
  if [[ $name == '' ]]; then
    echo "--name is required"
    exit 2
  fi
  # These are always derived from $name
  disk="${disk_dir}/${name}.raw"
  cidata="${disk_dir}/${name}-cidata.iso"
 
  local dom=cloudinit-$name
  echo "Will remove node: $dom"
  echo "Disk image:"
  ls -l "$disk"

  echo -n "OK? [y/N] "
  read yesno
  if [[ $yesno != "y" && $yesno != "yes" ]]; then
    echo "Cancelled."
    exit 1
  fi

  virsh destroy $dom
  virsh undefine $dom
  rm -f $disk $cidata
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
  echo "   Always in ${disk_base_dir}"
  echo "  --ram_mb <vm_ram_in_mb>"
  echo "  --cpus <cpu_count>"
  echo "  --keys_file <authorized_keys_file>"
  echo "  --user <default user>"
  echo "  --pass_hash <user_password_hash>"
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
