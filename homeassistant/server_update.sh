#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

sudo systemctl stop home-assistant@homeassistant

sudo -u homeassistant -H -- bash -c "cd /srv/homeassistant && source bin/activate && python3 -m pip install --upgrade homeassistant"

sudo systemctl start home-assistant@homeassistant
