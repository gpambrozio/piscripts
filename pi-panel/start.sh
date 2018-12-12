#!/bin/bash

# Turn off LED
# from https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi
echo none | sudo tee /sys/class/leds/led0/trigger
echo 1 | sudo tee /sys/class/leds/led0/brightness

SESSION_NAME="pi-panel"


screen -S $SESSION_NAME -t myWinName0 -A -d -m

screen -S $SESSION_NAME -p myWinName0 -X stuff $'cd /home/pi/pi-panel && sudo ./panelserver.py\n'
