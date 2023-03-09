#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

crontab $INSTALL_NAME/crontab.txt

# https://community.home-assistant.io/t/autostart-using-systemd/199497
sudo cp /home/pi/$INSTALL_NAME/homeassistant.service /etc/systemd/system/home-assistant@homeassistant.service
sudo systemctl --system daemon-reload
sudo systemctl enable home-assistant@homeassistant

sudo cp -f /home/pi/$INSTALL_NAME/smb.conf /etc/samba/
sudo systemctl restart smbd

sudo cp -f /home/pi/$INSTALL_NAME/nut/nut.conf /etc/nut/
sudo cp -f /home/pi/$INSTALL_NAME/nut/ups.conf /etc/nut/
sudo cp -f /home/pi/$INSTALL_NAME/nut/upsd.conf /etc/nut/
sudo cp -f /home/pi/$INSTALL_NAME/nut/upsd.users /etc/nut/
sudo systemctl restart nut-driver.service
sudo systemctl restart nut-server.service
sudo systemctl restart nut-monitor.service
