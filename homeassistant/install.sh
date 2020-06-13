#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# https://www.home-assistant.io/docs/installation/raspberry-pi/

sudo apt-get update
sudo apt-get upgrade -y

/home/pi/send-notification.sh "Setup 2 of 4"

sudo apt-get update
sudo apt-get install -y python3 python3-dev python3-venv python3-pip libffi-dev libssl-dev autoconf

sudo useradd -rm homeassistant -G dialout,gpio,i2c,pi
sudo mkdir /srv/homeassistant
sudo chown homeassistant:homeassistant /srv/homeassistant
sudo usermod -a -G homeassistant pi

/home/pi/send-notification.sh "Setup 3 of 4"

# Dropbox uploader: https://github.com/andreafabrizi/Dropbox-Uploader
curl "https://raw.githubusercontent.com/andreafabrizi/Dropbox-Uploader/master/dropbox_uploader.sh" -o /home/pi/dropbox_uploader.sh
TOKEN=`cat /boot/dropboxtoken`
echo "OAUTH_ACCESS_TOKEN=$TOKEN" > /home/pi/.dropbox_uploader
sudo cp .dropbox_uploader /root/.dropbox_uploader
sudo chmod +x /home/pi/dropbox_uploader.sh
sudo rm -f /boot/dropboxtoken

# For MQTT
sudo apt-get install -y mosquitto

# for https://www.home-assistant.io/integrations/nmap_tracker/
sudo apt-get install -y net-tools nmap

sudo -u homeassistant -H -- bash -c "mkdir /home/homeassistant/.homeassistant && cd /srv/homeassistant && python3 -m venv . && source bin/activate && python3 -m pip install wheel && pip3 install homeassistant"

/home/pi/send-notification.sh "Setup 4 of 4"

# https://community.home-assistant.io/t/autostart-using-systemd/199497
sudo mv /home/pi/homeassistant/homeassistant.service /etc/systemd/system/home-assistant@homeassistant.service
sudo systemctl --system daemon-reload
sudo systemctl enable home-assistant@homeassistant

sudo apt-get -y clean

# https://raspberrypi.stackexchange.com/a/66939

sudo raspi-config nonint do_hostname home
crontab homeassistant/crontab.txt
