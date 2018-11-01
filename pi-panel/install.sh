#!/bin/bash

cd /home/pi
sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y

git clone https://github.com/hzeller/rpi-rgb-led-matrix/
cd rpi-rgb-led-matrix/
make
make build-python
sudo make install-python

cd /home/pi
