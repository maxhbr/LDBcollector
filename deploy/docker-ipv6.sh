#!/bin/sh

# enable ipv6 for docker

set -e

# check am i root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# check if ipv6 is enabled in daemon.json
if test -x /etc/docker/daemon.json && grep -q '"ipv6"' /etc/docker/daemon.json; then
    echo "IPv6 is already configured."
    exit 0
fi

# enable ipv6
sed -i 's/"\}/
     "ipv6": true,
     "fixed-cidr-v6": "2001:db8:1::/64",
     "ip6tables": true,
     "experimental": true
    \}/g' /etc/docker/daemon.json
systemctl restart docker
