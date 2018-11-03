#!/bin/bash

SESSION_NAME="pi-panel"

screen -d -m -S $SESSION_NAME
screen -S $SESSION_NAME -p 0 -X stuff 'cd /home/pi/pi-panel && sudo ./panelserver.py
'

screen -S $SESSION_NAME -X screen 1
