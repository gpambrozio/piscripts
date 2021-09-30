#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 1"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

# https://github.com/vlachoudis/bCNC
cp -f /home/pi/cnc/bCNC.config /home/pi/.bCNC
sudo apt-get install -y python-imaging-tk python-opencv
pip install --upgrade bCNC

# To update firmware.
# from https://github.com/xinabox/xLoader#flashing-on-non-windows-operating-systems
sudo apt-get install -y avrdude

# Start automatically
# Form https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup#method-2-autostart
mkdir /home/pi/.config/autostart
cp /home/pi/cnc/bCNC.desktop /home/pi/.config/autostart/

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/cnc/smb.conf /etc/samba/
sudo systemctl restart smbd
/home/pi/send-notification.sh "Remember to run sudo smbpasswd -a pi to add user to samba"

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname cnc
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
sudo cp /home/pi/cnc/octoprint.service /etc/systemd/system/octoprint.service

sudo apt-get install -y libjpeg62-turbo-dev imagemagick ffmpeg libv4l-dev cmake
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer-experimental
export LD_LIBRARY_PATH=.
make
cd ../..
sudo cp /home/pi/cnc/webcamd.service /etc/systemd/system/webcamd.service

sudo systemctl daemon-reload
sudo systemctl enable octoprint.service
sudo systemctl enable webcamd.service

crontab cnc/crontab.txt
