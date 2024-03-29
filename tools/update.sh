#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

cp -f /home/pi/$INSTALL_NAME/bCNC.desktop /home/pi/.config/autostart/
cp -f /home/pi/$INSTALL_NAME/vlc.desktop /home/pi/.config/autostart/
sudo cp -f /home/pi/$INSTALL_NAME/smb.conf /etc/samba/

sudo cp /home/pi/$INSTALL_NAME/octoprint.service /etc/systemd/system/octoprint.service
sudo cp /home/pi/$INSTALL_NAME/camera-streamer.service /etc/systemd/system/camera-streamer.service

sudo systemctl daemon-reload
sudo systemctl enable octoprint.service
sudo systemctl enable camera-streamer.service

crontab $INSTALL_NAME/crontab.txt
