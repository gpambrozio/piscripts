#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

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
cat /home/pi/pictureframe/credentials.json | sed "s/CLIENT_SECRET/$SECRET/" > /home/pi/MagicMirror/modules/MMM-GooglePhotos/credentials.json

cp /home/pi/pictureframe/config.js /home/pi/MagicMirror/config/config.js
cp /home/pi/pictureframe/custom.css /home/pi/MagicMirror/css/custom.css

cd /home/pi
sudo npm install -g pm2
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u pi --hp /home/pi
chmod +x pictureframe/mm.sh
pm2 start pictureframe/mm.sh

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname pictureframe
sudo raspi-config nonint do_vnc 0

crontab pictureframe/crontab.txt

/home/pi/send-notification.sh "You need to run cd ~/MagicMirror/modules/MMM-GooglePhotos && node generate_token.js on the desktop"
