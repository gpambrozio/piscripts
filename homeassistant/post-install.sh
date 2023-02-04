#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

sudo smbpasswd -a pi
sudo update-alternatives --config python
