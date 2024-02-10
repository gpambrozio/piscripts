#!/bin/bash

set -xeuo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

# Install nut (https://networkupstools.org/)
sudo apt-get install -y nut

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname nut
