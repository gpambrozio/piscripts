#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

/home/pi/send-notification.sh "Setup 2 of 4"

# Cleanup

sudo apt-get -y clean

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname pictureframe

crontab pictureframe/crontab.txt
