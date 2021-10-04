#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

cp /home/pi/$INSTALL_NAME/config.js /home/pi/MagicMirror/config/config.js
cp /home/pi/$INSTALL_NAME/custom.css /home/pi/MagicMirror/css/custom.css

crontab $INSTALL_NAME/crontab.txt

