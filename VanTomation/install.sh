#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

didError () {
    errcode=$? # save the exit code as the first thing done in the trap function
    echo "error $errorcode"
    echo "the command executing at the time of the error was"
    echo "$BASH_COMMAND"
    echo "on line ${BASH_LINENO[0]}"
	/home/pi/send-notification.sh "Error happend during install"
    exit $errcode  # or use some other value or do return instead
}
trap didError ERR

cd /home/pi

# Bluepy: https://github.com/IanHarvey/bluepy
sudo apt-get install -y python-pip libglib2.0-dev
sudo pip install bluepy

# Installing nodejs
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs

# Bleno (for bt peripheral)
# Do this before bluez as it will be updated by better bluez bellow
cd /home/pi/VanTomation
sudo apt-get install -y bluetooth bluez libbluetooth-dev libudev-dev
npm install bleno
cd /home/pi

/home/pi/send-notification.sh "Setup node done"

# Installing bluez
sudo apt-get install -y libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.50.tar.xz
tar xvf bluez-5.50.tar.xz

# This path disables the second adapter as it is used by bleno directly
cp -f VanTomation/config/adapter.c bluez-5.50/src/
cd bluez-5.50
./configure
make
sudo make install
sudo systemctl enable bluetooth
sudo sh -c 'sed --in-place "s/blutoothd/bluetoothd --experimental/" /lib/systemd/system/bluetooth.service'

cd /home/pi

/home/pi/send-notification.sh "Setup bluez done"

sudo sh -c 'echo "hdmi_ignore_hotplug=1" >> /boot/config.txt'
sudo sh -c 'echo "sdtv_mode=0" >> /boot/config.txt'
sudo sh -c 'echo "enable_uart=1" >> /boot/config.txt'

# https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

sudo apt-get install -y hostapd dnsmasq
sudo cp VanTomation/config/iptables.ipv4.nat /etc/
sudo cp -f VanTomation/config/hostapd /etc/default/hostapd

PASS=`cat /home/pi/wifipass`
sed "s/PASSWORD/$PASS/" VanTomation/config/hostapd.conf > VanTomation/config/hostapd.conf.replaced
sudo mv -f VanTomation/config/hostapd.conf.replaced /etc/hostapd/hostapd.conf
rm /home/pi/wifipass

sudo cp -f VanTomation/config/interfaces.ap /etc/network/interfaces
sudo cp -f VanTomation/config/dhcpcd.ap /etc/dhcpcd.conf
sudo cp -f VanTomation/config/dnsmasq.conf /etc/dnsmasq.conf

sudo update-rc.d hostapd enable

sudo sh -c 'echo "iptables-restore < /etc/iptables.ipv4.nat" >> /etc/rc.local'
sudo sh -c 'echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf'

crontab VanTomation/config/crontab.txt
