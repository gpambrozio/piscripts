#!/bin/bash

SESSION_NAME="van"

sleep 5

screen -S $SESSION_NAME -t myWinName0 -A -d -m
screen -S $SESSION_NAME -X screen -t myWinName1

screen -S $SESSION_NAME -p myWinName0 -X stuff $'cd /home/pi/VanTomation/server && sudo ./vantomation.py\n'

# Wait a bit to start the second script as it kinda depends on the first
sleep 20
screen -S $SESSION_NAME -p myWinName1 -X stuff $'cd /home/pi/VanTomation && sudo BLENO_HCI_DEVICE_ID=1 node peripheral.js\n'
