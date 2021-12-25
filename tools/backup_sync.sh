#!/bin/bash

rclone sync /home/pi/.bCNC ha:piscripts/tools/bCNC.config --config /home/pi/.config/rclone/rclone.conf
rclone sync /home/pi/gcode/ ha:piscripts/tools/gcode/ --config /home/pi/.config/rclone/rclone.conf
rclone sync /home/pi/Desktop/ ha:piscripts/tools/Desktop/ --config /home/pi/.config/rclone/rclone.conf
rclone sync /home/pi/.share/local/ ha:piscripts/tools/localshare/ --config /home/pi/.config/rclone/rclone.conf
