#!/bin/bash


# Every once in a while the router stops resolving home.local. Doing a ping from the device
# seems to solve the issue so we do it periodically.
ping -c1 home.local > /dev/null

# From https://weworkweplay.com/play/rebooting-the-raspberry-pi-when-it-loses-wireless-connection-wifi/

ping -c4 192.168.86.1 > /dev/null
 
if [ $? != 0 ] 
then
  sudo ifconfig wlan0 down
  sleep 5
  sudo ifconfig wlan0 up
fi
