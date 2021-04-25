#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

sudo apt-get update
sudo apt-get upgrade -y

/home/pi/send-notification.sh "Setup 2 of 4"

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/doorbell/smb.conf /etc/samba/
sudo systemctl restart smbd
/home/pi/send-notification.sh "Remember to run sudo smbpasswd -a pi to add user to samba"

# Cleanup

sudo apt-get -y clean

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname doorbell

crontab doorbell/crontab.txt
