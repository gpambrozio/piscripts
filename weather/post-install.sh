#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

sudo smbpasswd -a pi
