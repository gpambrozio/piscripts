#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

sudo apt-get install python2.7-dev python-pillow -y

/home/pi/send-notification.sh "Setup 2 of 4"

cd /home/pi

git clone https://github.com/hzeller/rpi-rgb-led-matrix/
/home/pi/send-notification.sh "Setup 3 of 4"
cd rpi-rgb-led-matrix/
make

/home/pi/send-notification.sh "Setup 4 of 4"
make build-python
sudo make install-python

crontab pi-panel/crontab.txt
