#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

# We need to disable IPV6 otherwise a lot of things doesn't work (like notifications)
# From https://askubuntu.com/a/38468
sudo sh -c 'echo "precedence ::ffff:0:0/96  100" >> /etc/gai.conf'

cd /home/pi
wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/send-notification.sh
chmod +x send-notification.sh
/home/pi/send-notification.sh "Setup started"

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/bash_aliases.sh
mv -f bash_aliases.txt ~/.bash_aliases
chmod +x ~/.bash_aliases
