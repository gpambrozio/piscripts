#!/bin/bash

SESSION_NAME="doorbell"

screen -S $SESSION_NAME -t ha -A -d -m
screen -S $SESSION_NAME -X screen -t peripheral
screen -S $SESSION_NAME -X screen -t stream

screen -S $SESSION_NAME -p ha -X stuff $'cd /home/pi/doorbell && ./doorbell.py\n'
screen -S $SESSION_NAME -p stream -X stuff $'cd /home/pi/doorbell && ./stream.sh\n'
