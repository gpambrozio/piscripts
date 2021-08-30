#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

/home/pi/send-notification.sh "Setup 2 of 4"

# https://github.com/vlachoudis/bCNC
pip install --upgrade bCNC





# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname cnc

crontab doorbell/crontab.txt
