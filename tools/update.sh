#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

cp -f /home/pi/cnc/bCNC.config /home/pi/.bCNC
cp -f /home/pi/cnc/bCNC.desktop /home/pi/.config/autostart/
sudo cp -f /home/pi/cnc/smb.conf /etc/samba/

sudo cp /home/pi/cnc/octoprint.service /etc/systemd/system/octoprint.service
sudo cp /home/pi/cnc/webcamd.service /etc/systemd/system/webcamd.service

sudo systemctl daemon-reload
sudo systemctl enable octoprint.service
sudo systemctl enable webcamd.service

crontab cnc/crontab.txt
