#!/bin/bash

# From https://askubuntu.com/a/1005738
# Runs on dhcp hooks
syslog warn "Will run for _${reason}_"
if [ "${reason}" = "BOUND" ] ; then
    sleep 5
    /home/pi/VanTomation/dropbox_sync.sh
fi
