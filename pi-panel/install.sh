#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

sudo apt-get install python2.7-dev python-pillow -y

cd /home/pi

git clone https://github.com/hzeller/rpi-rgb-led-matrix/
cd rpi-rgb-led-matrix/
make

make build-python
sudo make install-python

sudo pip install paho-mqtt
