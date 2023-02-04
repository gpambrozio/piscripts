#!/bin/bash
 
# Based on https://github.com/DubhAd/Home-AssistantConfig/blob/live/local/bin/build_python

set -xeuo pipefail

PY_VER=${1}
VENV_BASE=/srv/homeassistant

python -m venv ${VENV_BASE}/venv_${PY_VER}
source ${VENV_BASE}/venv_${PY_VER}/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools

python -m pip install wheel

# to fix miniaudio issues: https://github.com/home-assistant/core/issues/66378#issuecomment-1040059972
python -m pip install --ignore-installed miniaudio --no-cache-dir --force-reinstall --no-binary :all:

python -m pip install -r /home/homeassistant/requirements.txt
python -m pip install --upgrade homeassistant
