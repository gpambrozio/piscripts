#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 1"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

# https://github.com/vlachoudis/bCNC
cp -f /home/pi/cnc/bCNC.config /home/pi/.bCNC
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

crontab cnc/crontab.txt
