function systemd_wrap() {
  systemd-run --user --scope -p "Delegate=yes" -- "$@"
}

function get_container_ip() {
  local container=$1
  return $(systemd_wrap lxc-ls -f -F NAME,IPV4 | awk "\$1==\"$NAME\" { print \$2; }")
}

function lxc_create() {
  local name=$1
  local dist=$2
  local release=$3
  local arch=$4
  local variant=$5
  systemd_wrap lxc-create -t download -n "${name}" \
    -- --dist "${dist}" --release "${release}" --arch "${arch}" --variant "${variant}"
}

function lxc_start() {
  local name=$1
  systemd_wrap lxc-start "${name}"
}

export LXC_AUTHORIZED_KEYS=$(cat $HOME/.ssh/authorized_keys)
