#!/bin/bash
# A helper for creating cloud-init VMs with libvirt.
# The intended use case is to make it easy to spin up disposable VMs.
#
# We take a handful of arguments as environment variables. Optionally, the
# first argument may be "--delete" to delete a VM.
#
# There is some global configuration below that specifies where to look for #
# disk images, and where to put the resulting VM images. Adjust as necessary.
#
# *** BEWARE ***
# We make a *bunch* of guesses about how the VM should be configured, and then
# set a default username/password! If you want to change that, you can specify
# a custom cloud-init file, which will override lots of the other options.
#
# Example usage:
#   Start a VM called "node0":
#     cloudinit.sh 
#   Delete "node0":
#     cloudinit.sh --delete
#   Specify name and VM size:
#     CLOUDINIT_RAM_MB=512
#     CLOUDINIT_CPUS=1
#     CLOUDINIT_NODE_NAME=mynode
#     cloudinit.sh

### START OF GLOBAL CONFIGURATION ###
# General configuration -- edit this for your libvirt setup.
disk_dir=/var/lib/virt/cloud-init/disks
live_dir=/var/lib/virt/cloud-init
### END OF GLOBAL CONFIGURATION ###

# We take arguments via environment variables because we're lazy.
node_name=${CLOUDINIT_NODE_NAME:-node0}
disk=${CLOUDINIT_DISK:-xenial-server-cloudimg-amd64-disk1.img}
dry_run=${CLOUDINIT_DRY_RUN:-no}
ram_mb=${CLOUDINIT_RAM_MB:-1024}
cpus=${CLOUDINIT_CPUS:-2}
cloud_init_file=${CLOUDINIT_FILE:-}
domain=${CLOUDINIT_DOMAIN:-$(hostname -d)}
ssh_key_file=${CLOUDINIT_SSH_KEY:-$HOME/authorized_keys}
os_variant=${CLOUDINIT_OS_VARIANT:-debian7}

# Sanity checks
if [[ ! -d "${disk_dir}" ]]; then
  echo "disk_dir $disk_dir (for disk cloud images) does not exist. Exiting."
  exit 1
fi
if [[ ! -d "${live_dir}" ]]; then
  echo "live_dir $live_dir (for VM images) does not exist. Exiting."
  exit 1
fi

for bin in genisoimage virt-install; do
  which $bin >/dev/null 2>&1
  if [[ "$?" != "0" ]]; then
    echo "Cannot find required program $bin. Aborting."
    exit 1
  fi
done

action="create"
if [[ "$1" = "--delete" ]]; then
  action="delete"
elif [[ -n "$1" ]]; then
  echo "Unknown argument $1"
  exit 2
fi

# Figure out all the paths of things we'll use or create
disk_path="${disk_dir}/${disk}"
live_path="${live_dir}/${node_name}.raw"
ci_iso_dir=${live_dir}/${node_name}.cidata.d
md_path=${ci_iso_dir}/meta-data
ud_path=${ci_iso_dir}/user-data
ci_iso_path=${live_dir}/${node_name}.cidata.iso

ssh_key="$(head -n 1 ${ssh_key_file})"

# Print out a confirmation of what we'll do.
if [[ "${dry_run}" == "yes" ]]; then
  prefix="echo Would run: "
else
  prefix=""
fi

if [[ "${dry_run}" == "yes" ]]; then
  echo "*** DRY RUN ***"
fi
if [[ "${action}" == "delete" ]]; then
  echo "WILL DELETE:"
  echo "Node name: ${node_name}"
  echo "Live disk: ${live_path}"
  echo "Cloud-init disk: ${ci_iso_path}"
else
  echo "Node name: ${node_name}"
  echo "Node domain: ${domain}"
  echo "Source disk: ${disk_path}"
  echo "Live disk: ${live_path}"
  echo "RAM: ${ram_mb} MB"
  echo "CPUs: ${cpus}"
  echo "SSH key (from $ssh_key_file): ${ssh_key}"
  if [[ -n "${cloud_init_file}" ]]; then
    echo "Cloud-init file: ${cloud_init_file}"
  else
    echo "Using default cloud-init file (cloud/cloud123 user)"
  fi
  echo "Cloud-init source dir: ${ci_iso_dir}"
  echo "Cloud-init disk: ${ci_iso_path}"
fi

echo "Ok? [y/N]"
read resp
if [[ "${resp}" != "y" && "${resp}" != "Y" ]]; then
  echo "Aborted by user."
  exit 1
fi

if [[ "${action}" == "delete" ]]; then
  $prefix virsh destroy "${node_name}"
  $prefix virsh undefine "${node_name}" --remove-all-storage
  exit 0
fi

user=cloud
# This is just cloud123 :)
pass_hash='$6$saltsalt$wVzOxp139jXJm2bHzpMAu/52NJLuaPceqzdvGa./Pxu5.amCga/iJsPLejmOHcd6/EAsslzKy79a49nP85FMR0'

if [[ -n "${cloud_init_file}" ]]; then
  $prefix cp ${cloud_init_file} ${ud_path}
else
  $prefix cat <<_EOF_ > ${ud_path}
#cloud-config
preserve_hostname: False
hostname: ${node_name}
fqdn: ${node_name}.${domain}
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
fi

echo "User-data:"
$prefix cat ${ud_path}

$prefix cp "${disk_path}" "${live_path}"
echo "instance-id: $node_name; local-hostname: $node_name" > ${md_path}

# The path is important here because we want to reference meta-data and
# user-data by their basenames. (There might be some sort of base dir option we
# can pass to genisoimage instead.)
$prefix mkdir ${ci_iso_dir}
pushd ${ci_iso_dir}
$prefix genisoimage \
  -output ${ci_iso_path} \
  -volid cidata \
  -joliet \
  -rock meta-data user-data
popd

$prefix virt-install \
  --import \
  --name $node_name \
  --ram ${ram_mb} \
  --vcpus ${cpus} \
  --disk $live_path \
  --noautoconsole \
  --graphics vnc \
  --disk ${ci_iso_path},device=cdrom \
  --network bridge=virbr0 \
  --os-type=linux \
  --os-variant=${os_variant}

