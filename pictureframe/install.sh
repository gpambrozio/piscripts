#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

/home/pi/send-notification.sh "Setup 1 of 4"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

/home/pi/send-notification.sh "Setup 2 of 4"

# picture frame
# https://www.tomshardware.com/how-to/raspberry-pi-photo-frame

curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt install -y nodejs
git clone https://github.com/MichMich/MagicMirror
cd MagicMirror
npm install
cd modules
git clone https://github.com/eouia/MMM-GooglePhotos.git
cd MMM-GooglePhotos
npm install

SECRET=`cat /boot/googlesecret`
sudo rm -f /boot/googlesecret
cat /home/pi/$INSTALL_NAME/credentials.json | sed "s/CLIENT_SECRET/$SECRET/" > /home/pi/MagicMirror/modules/MMM-GooglePhotos/credentials.json

cd /home/pi
sudo npm install -g pm2
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u pi --hp /home/pi
chmod +x $INSTALL_NAME/mm.sh
pm2 start $INSTALL_NAME/mm.sh

# https://github.com/MichMich/MagicMirror/wiki/Configuring-the-Raspberry-Pi#autohiding-the-mouse-pointer
sudo apt-get install -y unclutter
sudo sh -c 'echo "@unclutter -display :0 -idle 3 -root -noevents" >> /etc/xdg/lxsession/LXDE-pi/autostart'

# To be able to control monitor
sudo apt install -y ddcutil
sudo sh -c 'echo "dtoverlay=vc4-kms-v3d" >> /boot/config.txt'

# To control the monitor from HA
pip3 install paho-mqtt

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname $INSTALL_NAME
sudo raspi-config nonint do_vnc 0
