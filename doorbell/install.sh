#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

/home/pi/send-notification.sh "Setup 1 of 4"

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

/home/pi/send-notification.sh "Setup 2 of 4"

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/doorbell/smb.conf /etc/samba/
sudo systemctl restart smbd
/home/pi/send-notification.sh "Remember to run sudo smbpasswd -a pi to add user to samba"

# Motioneye
# https://github.com/ccrisan/motioneye/wiki/Install-On-Debian
sudo apt-get install -y motion ffmpeg v4l-utils
sudo apt-get install -y python-pip python-dev python-setuptools curl libssl-dev libcurl4-openssl-dev libjpeg-dev libz-dev
sudo apt-get install -y python-pil
sudo pip install motioneye

sudo mkdir -p /etc/motioneye /var/lib/motioneye
sudo cp -f /home/pi/doorbell/config/* /etc/motioneye/

sudo cp /usr/local/share/motioneye/extra/motioneye.systemd-unit-local /etc/systemd/system/motioneye.service
sudo systemctl daemon-reload
sudo systemctl enable motioneye

# GPIO
sudo apt-get install -y wiringpi
sudo apt-get install -y python3-gpiozero

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname doorbell

# https://raspberrypi.stackexchange.com/a/109221
# raspi-config nonint do_camera %d
# %d - Integer input - 0 is in general success / yes / selected, 1 is failed / no / not selected
sudo raspi-config nonint do_camera 0

# Fixes ir camera color
# https://www.raspberrypi.org/forums/viewtopic.php?f=43&t=245994
sudo sh -c 'echo "awb_auto_is_greyworld=1" >> /boot/config.txt'

crontab doorbell/crontab.txt
