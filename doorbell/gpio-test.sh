#!/bin/bash

gpio pwmr 1024
gpio -g mode 12 pwm
gpio -g mode 26 up

while [ 1 ] ; do
  gpio -g pwm 12 1024
  gpio readall
  sleep 1
  gpio -g pwm 12 512
  gpio readall
  sleep 1
  gpio -g pwm 12 0
  gpio readall
  sleep 1
done
