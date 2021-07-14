#/bin/bash
echo Installing as Service
CONFIG=./cutepihole.ini
if [[ "$(whoami)" != root ]]; then
  echo "Run this script as root!"
  exit 1
fi
if [! -f "$CONFIG"]; then
    exit 1
fi
mv ./cutepihole.service /etc/systemd/system
systemctl daemon-reload
systemctl start cutepihole.service
