#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

echo "Entre samba password:"
sudo smbpasswd -a pi

echo "Enter new pi password"
passwd
