#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

# http://weewx.com/docs/debian.htm

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

# MQTT extension for weewx
# https://github.com/weewx/weewx/wiki/mqtt
cd /home/pi
sudo apt install -y python3-pip
wget -O weewx-mqtt.zip https://github.com/matthewwall/weewx-mqtt/archive/master.zip
sudo pip3 install paho-mqtt
sudo wee_extension --install weewx-mqtt.zip
sudo rm -f weewx-mqtt.zip

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname weather

crontab weather/crontab.txt
