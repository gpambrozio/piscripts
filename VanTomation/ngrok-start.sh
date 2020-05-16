#!/bin/bash

DIR="/home/pi"

"${DIR}/ngrok" start --config "${DIR}/.ngrok2/ngrok.yml" ssh
