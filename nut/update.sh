#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

crontab $INSTALL_NAME/crontab.txt

sudo cp -f /home/pi/$INSTALL_NAME/nut/nut.conf /etc/nut/
sudo cp -f /home/pi/$INSTALL_NAME/nut/ups.conf /etc/nut/
sudo cp -f /home/pi/$INSTALL_NAME/nut/upsd.conf /etc/nut/
sudo cp -f /home/pi/$INSTALL_NAME/nut/upsmon.conf /etc/nut/
sudo cp -f /home/pi/$INSTALL_NAME/nut/upsd.users /etc/nut/
sudo systemctl restart nut-driver.service
sudo systemctl restart nut-server.service
sudo systemctl restart nut-monitor.service
