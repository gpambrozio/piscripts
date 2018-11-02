#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

sudo apt-get install python2.7-dev python-pillow -y

/home/pi/send-notification.sh "Setup 1 of 3"

cd /home/pi

git clone https://github.com/hzeller/rpi-rgb-led-matrix/
/home/pi/send-notification.sh "Setup 2 of 3"
cd rpi-rgb-led-matrix/
make

/home/pi/send-notification.sh "Setup 3 of 3"
make build-python
sudo make install-python
