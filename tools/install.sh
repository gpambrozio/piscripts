#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

INSTALL_NAME=`cat /home/pi/install_name`

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

# https://itheo.tech/ultimate-python-installation-on-a-raspberry-pi-ubuntu-script/
sudo apt-get install -y python-imaging-tk python-opencv python-paho-mqtt
sudo apt-get install -y python-tk python3-tk tk-dev

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/python.sh
chmod +x python.sh
sudo ./python.sh 3.11.0

# https://github.com/vlachoudis/bCNC
pip install --upgrade git+https://github.com/gpambrozio/bCNC.git@gustavo2
pip install paho-mqtt

# Start automatically
# Form https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup#method-2-autostart
mkdir -p /home/pi/.config/autostart

# Samba, from https://pimylifeup.com/raspberry-pi-samba/
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y samba samba-common-bin
sudo cp -f /home/pi/$INSTALL_NAME/smb.conf /etc/samba/
sudo systemctl restart smbd

# rclone to cloud upload/download/sync
curl https://rclone.org/install.sh | sudo bash
TOKEN=`cat /boot/dropboxtoken`
sudo rm -f /boot/dropboxtoken
mkdir -p /home/pi/.config/rclone
cat /home/pi/$INSTALL_NAME/rclone.conf | sed "s/TOKEN/$TOKEN/" > /home/pi/.config/rclone/rclone.conf

# rclone restore
sudo rclone copy ha:piscripts/$INSTALL_NAME/bCNC.config /home/pi/ --config /home/pi/.config/rclone/rclone.conf
sudo mv /home/pi/bCNC.config /home/pi/.bCNC
sudo chown pi:pi /home/pi/.bCNC
sudo chmod o+w /home/pi/.bCNC
mkdir /home/pi/gcode/

sudo rclone copy ha:piscripts/$INSTALL_NAME/gcode/ /home/pi/gcode/ --config /home/pi/.config/rclone/rclone.conf
sudo rclone copy ha:piscripts/$INSTALL_NAME/Desktop/ /home/pi/Desktop/ --config /home/pi/.config/rclone/rclone.conf
sudo rclone copy ha:piscripts/$INSTALL_NAME/localshare/ /home/pi/.local/share/ --config /home/pi/.config/rclone/rclone.conf
sudo rclone copy ha:piscripts/$INSTALL_NAME/config/ /home/pi/.config/ --config /home/pi/.config/rclone/rclone.conf

# https://raspberrypi.stackexchange.com/a/66939
sudo raspi-config nonint do_hostname $INSTALL_NAME
sudo raspi-config nonint do_vnc 0
sudo raspi-config nonint do_camera 0

# https://raspberrypi.stackexchange.com/a/87185
sudo timedatectl set-timezone Pacific/Honolulu

# No power saving for wifi
sudo iwconfig wlan0 power off

# octopi, from https://octoprint.org/download/ and 
# https://community.octoprint.org/t/setting-up-octoprint-on-a-raspberry-pi-running-raspbian-or-raspberry-pi-os/2337
mkdir OctoPrint
cd OctoPrint
python3 -m venv venv
source venv/bin/activate
pip install pip --upgrade
pip install octoprint
cd ..

sudo usermod -a -G tty pi
sudo usermod -a -G dialout pi

sudo apt-get install -y libjpeg62-turbo-dev imagemagick ffmpeg libv4l-dev cmake
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer-experimental
export LD_LIBRARY_PATH=.
make
cd ../..

# screen resolution
# Based on https://github.com/UCTRONICS/UCTRONICS_HDMI_CTS/blob/master/uc586/hdmi_480x800_cfg.sh
sudo sh -c 'echo "
# Screen resolution
hdmi_force_hotplug=1
max_usb_current=1
hdmi_group=2
hdmi_mode=16
hdmi_cvt 800 480 60 6 0 0 0
hdmi_drive=1" >> /boot/config.txt'

# To stream the desktop
# See https://gist.github.com/atlury/16e5994b1a97aad261275b612ba2470f
sudo apt-get install -y vlc vlc-plugin-access-extra

# To update board's firmware (via octoprint plugin https://github.com/OctoPrint/OctoPrint-FirmwareUpdater/blob/master/doc/avrdude.md)
sudo apt-get install -y avrdude

# Install octodash (https://github.com/UnchartedBull/OctoDash/wiki/Installation#manual-installation)
sudo apt-get install -y libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libuuid1 libappindicator3-1 libsecret-1-0 gir1.2-gnomekeyring-1.0
wget -O octodash.deb https://github.com/UnchartedBull/OctoDash/releases/download/v2.3.1/octodash_2.3.1_armv7l.deb
sudo dpkg -iy octodash.deb
