#!/bin/bash
# Creates a borg backup of a running libvirt VM backed by LVM. (This won't work
# for VMs backed by other storage types!)
#
# The goal is to make a simple VM backup that can be restored at the hypervisor
# level in one shot. It will be a large and clunky backup, and does not allow
# for single-file restores. This is meant to help you recover from catastrophic
# failures on your hypervisor.
# 
# The outline is this:
# - Dump the XML configuration of the VM to disk
# - Make an LVM snapshot of all disks associated with the VM
# - Copy the LVM snapshots and XML configuration to a new borg archive
#
# That's it!
#
# Here are the references I found helpeful while writing this:
# - https://blog.devzero.be/post/kvm-live-vm-backup/
# - https://borgbackup.readthedocs.io/en/stable/deployment/image-backup.html

set -u
set -e

# === Functions ===
function help_and_exit() {
  echo "Usage:"
  echo "  $0 [options] --name <vm_name>"
  echo "Options:"
  echo "--help  Show this help"
  echo "--dry-run  Display commands, don't do anything"
  echo "--borg-env-file <file>"
  echo "  Source this file before running borg. In this file, you must set:"
  echo "    BORG_REPO"
  echo '  because we will not provide them on the command line!'
  echo "  You probably also want to set BORG_PASSPHRASE or BORG_PASSCOMMAND to"
  echo "  avoid being prompted for a passphrase."
  echo "--snap-size <size>"
  echo "  How much space to allocate to the snapshot. (It is COW, so you need"
  echo "  to allocate only as much as you'll write while the snapshot exists.)"
  echo "  We accept any units LVM understands, such as 'b', 'M', and 'G'."
  echo "--backup-dir <directory>"
  echo "  Where to store backup files temporarily. We only use this for the"
  echo "  domain's xml configuration file -- no disk snapshots go here."
  echo "--exclude-devs <pattern>"
  echo "  A pattern given to grep -E; any devices matching this will be"
  echo "  EXCLUDED from the backup. You can test your patterns with --dry-run."
  exit 1
}

function do_snapshot() {
  backup_xml="${backup_dir}/${vm_name}.xml"
  
  if [[ -n $PREFIX ]]; then
    echo "*** DRY RUN MODE ***"
  fi

  vm_lvs=$(virsh domblklist "${vm_name}" | \
    awk '/^-----/{p=1} p{print $2}' | \
    grep -Ev "${exclude_devs}")

  # Sanity check - do all the devices we're backing up look like LVM devices?
  # (Future work: Do something more correct here and compare against
  # lvdisplay.)
  for lv_dev in ${vm_lvs}; do
    if [[ ${lv_dev:0:5} != "/dev/" ]]; then
      echo "Device ${lv_dev} on ${vm_name} does not look like LVM device."
      echo "You can use --exclude-devs to exclude particular devices."
      echo "Aborting."
      exit 1
    fi
  done
  
  virsh dumpxml --migratable "${vm_name}" > "${backup_xml}"
  snap_lvs=()
  for lv_dev in ${vm_lvs}; do
    snap_lv_dev="${lv_dev}-snap"
    echo "Snapshotting ${lv_dev}..."
    $PREFIX lvcreate --size "${snap_size}" --snapshot "${lv_dev}" -n "${snap_lv_dev}"
    snap_lvs+=($snap_lv_dev)
  done

  if [[ ${#snap_lvs[@]} -eq 0 ]]; then
    echo 'WARNING: All devices excluded from backup. We will only back up the xml configuration!'
  fi

  $PREFIX borg create --verbose --progress --list --stats --read-special "::${vm_name}-{now}" ${snap_lvs[*]-} "${backup_xml}"

  if [[ ${#snap_lvs[@]} -gt 0 ]]; then
    echo "Removing snapshots..."
    $PREFIX lvremove ${snap_lvs[*]}
  fi
  $PREFIX rm -f "${backup_xml}"
}

# === Default values ===
vm_name=''
borg_env_file=$HOME/borg_backup_vars
snap_size=100M
backup_dir=/data/backups
# Default maches nothing
exclude_devs='$^'
PREFIX=''

# === Flag parsing ===
opts=$(getopt \
  --longoptions help,dry-run,name:,borg-env-file:,snap-size:,backup-dir:,exclude-devs: \
  --name "$(basename $0)" \
  --options "" \
  -- "$@")
eval set -- $opts

while [[ $# -gt 0 ]]; do
  case "$1" in
    # Operations
    --help)
      help_and_exit
      shift;;
    --dry-run)
      PREFIX="echo ==>"
      shift;;
    # Flags
    --name)
      vm_name=$2
      shift 2;;
    --borg-env-file)
      borg_env_file=$2
      shift 2;;
    --snap-size)
      snap_size=$2
      shift 2;;
    --backup-dir)
      backup_dir=$2
      shift 2;;
    --exclude-devs)
      exclude_devs=$2
      shift 2;;
    *)
      break;;
  esac
done
# === Error checking ===
if [[ -z $vm_name ]]; then
  echo "--name is required; see --help for usage"
  exit 2
fi

if [[ ! -f "${borg_env_file}" ]]; then
  echo "borg environment file ${borg_env_file} does not exist"
  exit 1
fi
. "${borg_env_file}"

if [[ -z "${BORG_REPO}" ]]; then
  echo "\$BORG_REPO is unset. Set it in ${borg_env_file}."
  exit 1
fi

do_snapshot
