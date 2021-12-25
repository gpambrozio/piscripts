#!/bin/bash

set -xeuo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

# https://www.home-assistant.io/docs/installation/raspberry-pi/

sudo apt-get update
sudo apt-get install -y python3 python3-dev python3-venv python3-pip libffi-dev libssl-dev autoconf

sudo useradd -rm homeassistant -G dialout,gpio,i2c,pi
sudo mkdir /srv/homeassistant
sudo chown homeassistant:homeassistant /srv/homeassistant
sudo usermod -a -G homeassistant pi

# rclone to cloud upload/download/sync
curl https://rclone.org/install.sh | sudo bash
TOKEN=`cat /boot/dropboxtoken`
sudo rm -f /boot/dropboxtoken
mkdir -p /home/pi/.config/rclone
cat /home/pi/$INSTALL_NAME/rclone.conf | sed "s/TOKEN/$TOKEN/" > /home/pi/.config/rclone/rclone.conf

# For MQTT
sudo apt-get install -y mosquitto mosquitto-clients

# for https://www.home-assistant.io/integrations/nmap_tracker/
sudo apt-get install -y net-tools nmap

# https://github.com/adafruit/Adafruit_CircuitPython_DHT/issues/29
sudo apt-get install -y libgpiod2

# https://community.home-assistant.io/t/cannot-update-to-2021-10-0/344695/3
wget https://sh.rustup.rs -O rustup-init.sh
chmod +x rustup-init.sh
sudo -u homeassistant -H -- bash -c "./rustup-init.sh -y"
sudo apt-get install -y libssl-dev rustc

# https://itheo.tech/ultimate-python-installation-on-a-raspberry-pi-ubuntu-script/
sudo bash /home/pi/$INSTALL_NAME/python.sh 3.9.9

# https://github.com/DubhAd/Home-AssistantConfig/blob/live/local/bin/build_python
sudo apt-get install -y libopenjp2-7 libtiff-dev unixodbc-dev

# Fixes error looking for newer library
sudo ln -s /usr/lib/arm-linux-gnueabihf/libffi.so.6 /usr/lib/arm-linux-gnueabihf/libffi.so.7

# Install ha in a venv
sudo -u homeassistant -H -- bash -c "/home/pi/$INSTALL_NAME/ha.sh 3.9.9"

# https://appdaemon.readthedocs.io/en/stable/INSTALL.html
sudo python -m pip install appdaemon
sudo mv /home/pi/$INSTALL_NAME/appdaemon.service /etc/systemd/system/appdaemon@appdaemon.service
sudo systemctl --system daemon-reload
sudo systemctl enable appdaemon@appdaemon.service

sudo -u homeassistant -H -- bash -c "mkdir /home/homeassistant/.homeassistant"
sudo rclone copy ha:piscripts/$INSTALL_NAME/homeassistant.conf/ /home/homeassistant/.homeassistant/ --config /home/pi/.config/rclone/rclone.conf
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant

# for keymaster
sudo -u homeassistant -H -- bash -c "source /srv/homeassistant/venv_3.9.9/bin/activate && pip install python-openzwave-mqtt"

# This installs a bunch of relevant packages automatically, speeding up first startup
sudo -u homeassistant -H -- bash -c "source /srv/homeassistant/venv_3.9.9/bin/activate && hass --script check_config"

# MySensors, from https://www.mysensors.org/build/raspberry
cd /home/pi
git clone https://github.com/mysensors/MySensors.git --branch master
cd MySensors
./configure --my-transport=rf24 --my-rf24-irq-pin=15
make
sudo make install
sudo systemctl enable mysgw.service
sudo systemctl start mysgw.service
cd ..

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y samba samba-common-bin

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname home

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu
