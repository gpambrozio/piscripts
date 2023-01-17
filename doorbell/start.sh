#!/bin/bash

SESSION_NAME="doorbell"

screen -S $SESSION_NAME -t server -A -d -m
screen -S $SESSION_NAME -p server -X ha $'cd /home/pi/doorbell && ./doorbell.py\n'
screen -S $SESSION_NAME -p server -X stream $'cd /home/pi/doorbell && ./stream.py\n'
