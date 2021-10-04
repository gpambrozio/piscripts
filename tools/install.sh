#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

# https://github.com/vlachoudis/bCNC
sudo apt-get install -y python-imaging-tk python-opencv
pip install --upgrade bCNC

# To update firmware.
# from https://github.com/xinabox/xLoader#flashing-on-non-windows-operating-systems
sudo apt-get install -y avrdude

# Start automatically
# Form https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup#method-2-autostart
mkdir /home/pi/.config/autostart

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/$INSTALL_NAME/smb.conf /etc/samba/
sudo systemctl restart smbd

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname $INSTALL_NAME
sudo raspi-config nonint do_vnc 1
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

# OctoPiPanel
# https://github.com/gpambrozio/OctoPiPanel.git
sudo sh -c 'echo "dtparam=spi=on" >> /boot/config.txt'
sudo sh -c 'echo "dtparam=i2c1=on" >> /boot/config.txt'
sudo sh -c 'echo "dtparam=i2c_arm=on" >> /boot/config.txt'
sudo sh -c 'echo "dtoverlay=pitft28-resistive,rotate=270,speed=64000000,fps=30" >> /boot/config.txt'

sudo sh -c 'echo "SUBSYSTEM==\"input\", ATTRS{name}==\"*stmpe*\", ENV{DEVNAME}==\"*event*\", SYMLINK+=\"input/touchscreen\"" >> /etc/udev/rules.d/95-stmpe.rules'
sudo rmmod stmpe_ts; sudo modprobe stmpe_ts

# From https://www.raspberrypi.org/forums/viewtopic.php?t=250001
wget https://www.dropbox.com/s/0tkdym8ojhcmbu2/libsdl1.2debian_1.2.15+veloci1-1_armhf.deb
sudo dpkg -i libsdl1.2debian_1.2.15+veloci1-1_armhf.deb
sudo apt-get -f -y install

git clone --branch devel https://github.com/gpambrozio/OctoPiPanel.git
cd OctoPiPanel
sudo pip install -r requirements.txt
sudo pip install evdev

chmod +x OctoPiPanel.py
sudo cp scripts/octopipanel.init /etc/init.d/octopipanel
sudo chmod +x /etc/init.d/octopipanel
sudo cp scripts/octopipanel.default /etc/default/octopipanel
sudo update-rc.d octopipanel defaults

# To calibrate
# See https://prajoshpremdas.wordpress.com/2016/09/30/calibrating-touch-using-tslib-in-linux/
sudo apt-get install -y libts-bin

cd ..
