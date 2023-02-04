#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

sudo systemctl stop home-assistant@homeassistant
pm2 stop homeassistant/zwavejs.sh

sudo npm install -g @zwave-js/server@latest
pm2 start homeassistant/zwavejs.sh

sudo -u homeassistant -H -- bash -c "export PATH=\"/home/homeassistant/.cargo/bin:$PATH\" && cd /srv/homeassistant/venv_3.10.9 && source bin/activate && pip install --upgrade pip && python3 -m pip install --upgrade homeassistant"
sudo systemctl start home-assistant@homeassistant

echo "Done."
echo ""
echo "To monitor server:"
echo ""
echo "journalctl -f -u home-assistant@homeassistant"
echo ""
