#!/bin/bash

SESSION_NAME="doorbell"

screen -S $SESSION_NAME -t ha -A -d -m
screen -S $SESSION_NAME -X screen -t peripheral

screen -S $SESSION_NAME -p ha -X stuff $'cd /home/pi/doorbell && sleep 10 && while [ 1 ] ; do ./doorbell.py ; sleep 5 ; done\n'
