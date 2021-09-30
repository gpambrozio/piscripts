#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

cp /home/pi/pictureframe/config.js /home/pi/MagicMirror/config/config.js
cp /home/pi/pictureframe/custom.css /home/pi/MagicMirror/css/custom.css

crontab pictureframe/crontab.txt

