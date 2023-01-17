#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/$INSTALL_NAME/smb.conf /etc/samba/
sudo systemctl restart smbd

# Motioneye
# https://github.com/motioneye-project/motioneye/wiki/Install-on-Raspbian-Bullseye
sudo apt-get install -y ffmpeg libmariadb3 libpq5 libmicrohttpd12
wget https://github.com/Motion-Project/motion/releases/download/release-4.3.2/pi_buster_motion_4.3.2-1_armhf.deb
sudo dpkg -i pi_buster_motion_4.3.2-1_armhf.deb

sudo systemctl stop motion
sudo systemctl disable motion

sudo apt-get install -y python2 python-dev-is-python2
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
sudo python2 get-pip.py
sudo apt-get install -y libssl-dev libcurl4-openssl-dev libjpeg-dev zlib1g-dev
sudo pip2 install motioneye

sudo mkdir -p /etc/motioneye /var/lib/motioneye

sudo cp /usr/local/share/motioneye/extra/motioneye.systemd-unit-local /etc/systemd/system/motioneye.service
sudo systemctl daemon-reload
sudo systemctl enable motioneye

# GPIO
sudo apt-get install -y python3-gpiozero

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname $INSTALL_NAME

# https://raspberrypi.stackexchange.com/a/109221
# raspi-config nonint do_camera %d
# %d - Integer input - 0 is in general success / yes / selected, 1 is failed / no / not selected
sudo raspi-config nonint do_camera 0
