#!/bin/bash

rclone sync /home/homeassistant/.homeassistant/ ha:piscripts/homeassistant/homeassistant.conf/ --exclude "__pycache__/**" --exclude "home-assistant_v2.db*" --exclude "deps/**" --config /home/pi/.config/rclone/rclone.conf
