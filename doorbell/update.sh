#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

sudo cp -f /home/pi/$INSTALL_NAME/config/* /etc/motioneye/
crontab $INSTALL_NAME/crontab.txt
