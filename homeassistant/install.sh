#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# https://www.home-assistant.io/docs/installation/raspberry-pi/

/home/pi/send-notification.sh "Setup 2 of 4"

sudo apt-get update
sudo apt-get install -y python3 python3-dev python3-venv python3-pip libffi-dev libssl-dev autoconf

sudo useradd -rm homeassistant -G dialout,gpio,i2c,pi
sudo mkdir /srv/homeassistant
sudo chown homeassistant:homeassistant /srv/homeassistant
sudo usermod -a -G homeassistant pi

/home/pi/send-notification.sh "Setup 3 of 4"

# rclone to cloud upload/download/sync
sudo apt-get install -y rclone
TOKEN=`cat /boot/dropboxtoken`
sudo rm -f /boot/dropboxtoken
mkdir -p /home/pi/.config/rclone
cat /home/pi/homeassistant/rclone.conf | sed "s/TOKEN/$TOKEN/" > /home/pi/.config/rclone/rclone.conf

# For MQTT
sudo apt-get install -y mosquitto mosquitto-clients

# for https://www.home-assistant.io/integrations/nmap_tracker/
sudo apt-get install -y net-tools nmap

# https://github.com/adafruit/Adafruit_CircuitPython_DHT/issues/29
sudo apt-get install -y libgpiod2

sudo -u homeassistant -H -- bash -c "mkdir /home/homeassistant/.homeassistant && cd /srv/homeassistant && python3 -m venv . && source bin/activate && python3 -m pip install wheel && pip3 install homeassistant"

# https://appdaemon.readthedocs.io/en/stable/INSTALL.html
sudo pip3 install appdaemon
sudo mv /home/pi/homeassistant/appdaemon.service /etc/systemd/system/appdaemon@appdaemon.service
sudo systemctl --system daemon-reload
sudo systemctl enable appdaemon@appdaemon.service

sudo rclone copy ha:piscripts/homeassistant/homeassistant.conf/ /home/homeassistant/.homeassistant/ --config /home/pi/.config/rclone/rclone.conf
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant

/home/pi/send-notification.sh "Setup 4 of 4"

# https://community.home-assistant.io/t/autostart-using-systemd/199497
sudo mv /home/pi/homeassistant/homeassistant.service /etc/systemd/system/home-assistant@homeassistant.service
sudo systemctl --system daemon-reload
sudo systemctl enable home-assistant@homeassistant

# MySensors, from https://www.mysensors.org/build/raspberry
cd /home/pi
git clone https://github.com/mysensors/MySensors.git --branch master
cd MySensors
./configure --my-transport=rf24 --my-rf24-irq-pin=15
make
sudo make install
sudo systemctl enable mysgw.service
sudo systemctl start mysgw.service

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/homeassistant/smb.conf /etc/samba/
sudo systemctl restart smbd
/home/pi/send-notification.sh "Remember to run sudo smbpasswd -a pi to add user to samba"

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname home

crontab homeassistant/crontab.txt
