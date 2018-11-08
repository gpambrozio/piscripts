#!/bin/bash

SESSION_NAME="pi-panel"


screen -S $SESSION_NAME -t myWinName0 -A -d -m

screen -S $SESSION_NAME -p myWinName0 -X stuff $'cd /home/pi/pi-panel && sudo ./panelserver.py\n'
