#!/bin/bash

SESSION_NAME="van"

screen -d -m -S $SESSION_NAME
screen -S $SESSION_NAME -p 0 -X stuff 'cd /home/pi/VanTomation && sudo ./vantomation.py
'

screen -S $SESSION_NAME -X screen 1
screen -S $SESSION_NAME -p 1 -X stuff 'cd /home/pi/VanTomation && sudo BLENO_HCI_DEVICE_ID=1 node peripheral.js
'

screen -S $SESSION_NAME -X screen 2
