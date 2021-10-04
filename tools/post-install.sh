#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

sudo smbpasswd -a pi
sudo TSLIB_FBDEVICE=/dev/fb1 TSLIB_TSDEVICE=/dev/input/touchscreen ts_calibrate
