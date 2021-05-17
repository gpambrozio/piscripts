#!/bin/bash

SESSION_NAME="doorbell"

screen -S $SESSION_NAME -t server -A -d -m
screen -S $SESSION_NAME -p server -X stuff $'cd /home/pi/doorbell && ./doorbell.py\n'
