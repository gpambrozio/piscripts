#!/bin/bash
 
# Based on https://github.com/DubhAd/Home-AssistantConfig/blob/live/local/bin/build_python

set -euo pipefail

PY_VER=${1}
VENV_BASE=/srv/homeassistant

python3 -m venv ${VENV_BASE}/venv_${PY_VER}
source ${VENV_BASE}/venv_${PY_VER}/bin/activate
python3 -m pip install --upgrade homeassistant
# This installs a bunch of relevant packages automatically, speeding up first startup
hass --script check_config
# Now we install requirements
wget --quiet https://raw.githubusercontent.com/home-assistant/docker/master/requirements.txt -O - | while read LINE
do
  python3 -m pip install --upgrade ${LINE}
done
