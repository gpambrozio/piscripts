#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# http://weewx.com/docs/debian.htm

sudo apt-get update
sudo apt-get upgrade -y

wget -qO - https://weewx.com/keys.html | sudo apt-key add -
wget -qO - https://weewx.com/apt/weewx-python3.list | sudo tee /etc/apt/sources.list.d/weewx.list
sudo apt-get update
sudo apt-get install -y weewx

/home/pi/send-notification.sh "Setup 2 of 4"

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/weather/smb.conf /etc/samba/
sudo systemctl restart smbd
/home/pi/send-notification.sh "Remember to run sudo smbpasswd -a pi to add user to samba"

# Apache, to serve weewx
sudo apt-get install -y apache2

# Cleanup

sudo apt-get -y clean

# https://raspberrypi.stackexchange.com/a/66939

sudo raspi-config nonint do_hostname weather
crontab weather/crontab.txt
