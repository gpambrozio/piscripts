#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

# https://github.com/vlachoudis/bCNC
sudo apt-get install -y python-imaging-tk python-opencv
pip install --upgrade bCNC

# Start automatically
# Form https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup#method-2-autostart
mkdir /home/pi/.config/autostart

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/$INSTALL_NAME/smb.conf /etc/samba/
sudo systemctl restart smbd

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname $INSTALL_NAME
sudo raspi-config nonint do_vnc 0
sudo raspi-config nonint do_camera 0

# octopi, from https://octoprint.org/download/ and 
# https://community.octoprint.org/t/setting-up-octoprint-on-a-raspberry-pi-running-raspbian-or-raspberry-pi-os/2337
mkdir OctoPrint
cd OctoPrint
python3 -m venv venv
source venv/bin/activate
pip install pip --upgrade
pip install octoprint
cd ..

sudo usermod -a -G tty pi
sudo usermod -a -G dialout pi

sudo apt-get install -y libjpeg62-turbo-dev imagemagick ffmpeg libv4l-dev cmake
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer-experimental
export LD_LIBRARY_PATH=.
make
cd ../..
