#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

/home/pi/send-notification.sh "Setup 2 of 4"

# https://github.com/vlachoudis/bCNC
pip install --upgrade bCNC

# Start automatically
# Form https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup#method-2-autostart
mkdir /home/pi/.config/autostart
cp cnc/bCNC.desktop /home/pi/.config/autostart/

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname cnc
sudo raspi-config nonint do_vnc 0

crontab cnc/crontab.txt
