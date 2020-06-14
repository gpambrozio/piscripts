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

# rclone to cloud upload/download/sync
sudo apt-get install rclone
TOKEN=`cat /boot/dropboxtoken`
sudo rm -f /boot/dropboxtoken
mkdir -p /home/pi/.config/rclone
cat rclone.conf | sed "s/TOKEN/$TOKEN/" > /home/pi/.config/rclone/rclone.conf

# For MQTT
sudo apt-get install -y mosquitto

# for https://www.home-assistant.io/integrations/nmap_tracker/
sudo apt-get install -y net-tools nmap

sudo -u homeassistant -H -- bash -c "mkdir /home/homeassistant/.homeassistant && cd /srv/homeassistant && python3 -m venv . && source bin/activate && python3 -m pip install wheel && pip3 install homeassistant"

# https://appdaemon.readthedocs.io/en/stable/INSTALL.html
sudo pip3 install appdaemon
sudo mv /home/pi/homeassistant/appdaemon.service /etc/systemd/system/appdaemon@appdaemon.service
sudo systemctl --system daemon-reload
sudo systemctl enable appdaemon@appdaemon.service

# for https://hacs.xyz/docs/installation/manual
sudo -u homeassistant -H -- bash -c "mkdir -p /home/homeassistant/.homeassistant/custom_coponents/hacs && cd /home/homeassistant/.homeassistant/custom_coponents/hacs && wget https://github.com/hacs/integration/releases/latest/download/hacs.zip && unzip hacs.zip && rm hacs.zip"

/home/pi/send-notification.sh "Setup 4 of 4"

# https://community.home-assistant.io/t/autostart-using-systemd/199497
sudo mv /home/pi/homeassistant/homeassistant.service /etc/systemd/system/home-assistant@homeassistant.service
sudo systemctl --system daemon-reload
sudo systemctl enable home-assistant@homeassistant

sudo apt-get -y clean

# https://raspberrypi.stackexchange.com/a/66939

sudo raspi-config nonint do_hostname home
crontab homeassistant/crontab.txt
