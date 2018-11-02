#!/bin/bash

cd /home/pi
wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/send-notification.sh
chmod +x send-notification.sh
./send-notification.sh "Setup started"

sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y

./send-notification.sh "Setup 1 of 3"

git clone https://github.com/hzeller/rpi-rgb-led-matrix/
./send-notification.sh "Setup 2 of 3"
cd rpi-rgb-led-matrix/
make
./send-notification.sh "Setup 3 of 3"
make build-python
sudo make install-python

cd /home/pi

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/pi-panel/samplebase.py
wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/pi-panel/runtext.py
wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/pi-panel/9x15.bdf
chmod +x runtext.py

./send-notification.sh "Done. Rebooting."
rm send-notification.sh
