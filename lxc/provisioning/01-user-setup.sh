set -x

# ==========
# User setup
# ==========
# This should be distro-agnostic.

# This works because environment variables survive lxc-attach
/sbin/adduser --disabled-password --gecos "" $USER
mkdir -p /home/$USER/.ssh
chmod 0700 /home/$USER/.ssh
chown -R $USER:$USER /home/$USER/.ssh
echo "$USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/01-$USER
echo "$LXC_AUTHORIZED_KEYS" > /home/$USER/.ssh/authorized_keys

# ===========
# Weird hacks
# ===========
# See https://forum.proxmox.com/threads/ping-with-unprivileged-user-in-lxc-container-linux-capabilities.42308/
/sbin/setcap cap_net_raw+p /bin/ping
