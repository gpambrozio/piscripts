#!/bin/bash

rclone sync /home/pi/.bCNC ha:piscripts/tools/bCNC.config --config /home/pi/.config/rclone/rclone.conf
rclone sync /home/pi/gcode/ ha:piscripts/tools/gcode/ --config /home/pi/.config/rclone/rclone.conf
