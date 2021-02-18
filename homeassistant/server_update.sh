#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

sudo systemctl stop home-assistant@homeassistant

sudo -u homeassistant -H -- bash -c "cd /srv/homeassistant_venv_3.8.7 && source bin/activate && python3 -m pip install --upgrade homeassistant"

sudo systemctl start home-assistant@homeassistant

echo "Done."
echo ""
echo "To monitor server:"
echo ""
echo "journalctl -f -u home-assistant@homeassistant"
echo ""
