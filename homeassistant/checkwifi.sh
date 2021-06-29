#!/bin/bash

# From https://weworkweplay.com/play/rebooting-the-raspberry-pi-when-it-loses-wireless-connection-wifi/

ping -c4 192.168.86.1 > /dev/null
 
if [ $? != 0 ] 
then
  sudo ifconfig wlan0 down
  sleep 5
  sudo ifconfig wlan0 up
fi
