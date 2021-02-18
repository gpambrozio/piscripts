#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# http://weewx.com/docs/debian.htm

sudo apt-get update
sudo apt-get upgrade -y

wget -qO - https://weewx.com/keys.html | sudo apt-key add -
wget -qO - https://weewx.com/apt/weewx-python3.list | sudo tee /etc/apt/sources.list.d/weewx.list
sudo apt-get update
sudo apt-get install -y weewx

/home/pi/send-notification.sh "Setup 2 of 4"

# Cleanup

sudo apt-get -y clean

# https://raspberrypi.stackexchange.com/a/66939

sudo raspi-config nonint do_hostname weather
crontab weather/crontab.txt
