#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

NAME=`cat install_name`
cd "$NAME"
svn update
