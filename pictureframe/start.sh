#!/bin/bash

SESSION_NAME="pictureframe"

screen -S $SESSION_NAME -t pictureframe -A -d -m
screen -S $SESSION_NAME -p pictureframe -X stuff $'cd /home/pi/pictureframe && ./mqtt.py\n'
