#!/bin/bash

set -xeuo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

# https://www.home-assistant.io/docs/installation/raspberry-pi/

sudo apt-get update
sudo apt-get install -y python3 python3-dev python3-venv python3-pip libffi-dev libssl-dev autoconf libxslt1-dev libc6 bluez ffmpeg
sudo apt-get install -y libatlas-base-dev

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

# https://community.home-assistant.io/t/cannot-update-to-2021-10-0/344695/3
wget https://sh.rustup.rs -O rustup-init.sh
chmod +x rustup-init.sh
sudo -u homeassistant -H -- bash -c "/home/pi/rustup-init.sh -y"

# https://itheo.tech/ultimate-python-installation-on-a-raspberry-pi-ubuntu-script/
wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/python.sh
chmod +x python.sh
sudo ./python.sh 3.11.1

# https://github.com/DubhAd/Home-AssistantConfig/blob/live/local/bin/build_python
sudo apt-get install -y libopenjp2-7 libtiff-dev unixodbc-dev

# Fixes error looking for newer library
sudo ln -s /usr/lib/arm-linux-gnueabihf/libffi.so.6 /usr/lib/arm-linux-gnueabihf/libffi.so.7

# Needed this when installing ha for python 3.10
sudo apt-get install -y default-libmysqlclient-dev libudev-dev libpq-dev

# Install nut (https://networkupstools.org/)
sudo apt-get install -y nut

# Install ha in a venv
sudo -u homeassistant -H -- bash -c "/home/pi/$INSTALL_NAME/ha.sh 3.11.1"

# https://appdaemon.readthedocs.io/en/stable/INSTALL.html
sudo python -m pip install appdaemon
sudo mv /home/pi/$INSTALL_NAME/appdaemon.service /etc/systemd/system/appdaemon@appdaemon.service
sudo systemctl --system daemon-reload
sudo systemctl enable appdaemon@appdaemon.service

# For zwave-js
# NodeJS first
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# https://github.com/zwave-js/zwave-js-server
sudo npm i -g @zwave-js/server
NETWORK_KEY=`cat /boot/zwavekey`
sudo rm -f /boot/zwavekey
cat /home/pi/$INSTALL_NAME/zwavejs-config.js | sed "s/NETWORK_KEY/$NETWORK_KEY/" > /home/pi/.config/zwavejs-config.js

# To start on boot
sudo npm install -g pm2
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u pi --hp /home/pi
chmod +x $INSTALL_NAME/zwavejs.sh
pm2 start $INSTALL_NAME/zwavejs.sh
pm2 save

# Restore backup
sudo -u homeassistant -H -- bash -c "mkdir /home/homeassistant/.homeassistant"
sudo rclone copy ha:piscripts/$INSTALL_NAME/homeassistant.conf/ /home/homeassistant/.homeassistant/ --config /home/pi/.config/rclone/rclone.conf
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant

# for keymaster
sudo -u homeassistant -H -- bash -c "source /srv/homeassistant/venv_3.10.9/bin/activate && pip install python-openzwave-mqtt"

# for BME280
sudo -u homeassistant -H -- bash -c "source /srv/homeassistant/venv_3.10.9/bin/activate && pip install RPi.bme280"

# to fix numpy issues. https://stackoverflow.com/a/62084261
sudo -u homeassistant -H -- bash -c "source /srv/homeassistant/venv_3.10.9/bin/activate && pip3 install numpy --global-option=\"-mfloat-abi=hard\" --force-reinstall"

# This installs a bunch of relevant packages automatically, speeding up first startup
sudo -u homeassistant -H -- bash -c "source /srv/homeassistant/venv_3.10.9/bin/activate && hass --script check_config"

# Fix sqlite version
# https://community.home-assistant.io/t/raspberrypi-ha-core-version-3-27-2-of-sqlite-is-not-supported/352858/2?u=gpambrozio
cd /home/pi
wget https://sqlite.org/2021/sqlite-autoconf-3370100.tar.gz
tar -xvf sqlite-autoconf-3370100.tar.gz
rm sqlite-autoconf-3370100.tar.gz
cd sqlite-autoconf-3370100
./configure
make
sudo make install
sudo cp /usr/local/lib/*sql* /usr/lib/arm-linux-gnueabihf/
cd ..

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y samba samba-common-bin

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname home

# For BME280
sudo apt-get install -y python3-smbus
sudo -u homeassistant -H -- bash -c "source /srv/homeassistant/venv_3.10.9/bin/activate && pip install i2cdevice smbus"
sudo raspi-config nonint do_i2c 0

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu
