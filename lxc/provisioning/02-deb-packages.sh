set -x

# ===================================
# Basic system setup - debian version
# ===================================
apt-get update
apt-get upgrade -y
apt-get install -y openssh-server man curl python3

