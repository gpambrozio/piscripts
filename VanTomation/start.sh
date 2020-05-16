#!/bin/bash

SESSION_NAME="van"

sleep 5

screen -S $SESSION_NAME -t vantomation -A -d -m
screen -S $SESSION_NAME -X screen -t peripheral
screen -S $SESSION_NAME -X screen -t ngrok

screen -S $SESSION_NAME -p vantomation -X stuff $'cd /home/pi/VanTomation/server && sudo ./vantomation.py\n'
screen -S $SESSION_NAME -p ngrok -X stuff $'/home/pi/VanTomation/ngrok-start.sh\n'

# Wait a bit to start the second script as it kinda depends on the first
sleep 20
screen -S $SESSION_NAME -p peripheral -X stuff $'cd /home/pi/VanTomation && sudo BLENO_HCI_DEVICE_ID=1 node peripheral.js\n'
