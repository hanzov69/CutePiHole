#/bin/bash
echo Cloning latest release
CONFIG=./cutepihole.ini
if [[ "$(whoami)" != root ]]; then
  echo "Run this script as root!"
  exit 1
fi
if test [! -f "$CONFIG"]; then
    exit 1
fi
mv ./cutepihole.service /etc/systemd/system
systemctl daemon-reload
systemctl start cutepihole.service
