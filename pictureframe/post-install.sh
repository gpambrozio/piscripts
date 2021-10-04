#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

cd ~/MagicMirror/modules/MMM-GooglePhotos && node generate_token.js
