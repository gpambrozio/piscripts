#!/bin/bash

/home/pi/dropbox_uploader.sh -x "__pycache__" -x "deps" -x "home-assistant_v2.db" upload /home/homeassistant/.homeassistant/ homeassistant.conf
