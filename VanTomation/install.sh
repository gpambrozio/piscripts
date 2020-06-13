#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

didError () {
    errcode=$? # save the exit code as the first thing done in the trap function
    echo "error $errcode"
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
sudo pip install bluepy==1.1.4

# Stuff for monitor.sh
sudo pip install pillow
sudo pip install pyephem
sudo pip install pyowm
sudo apt-get install -y python-imaging-tk

# Installing nodejs
# From https://warlord0blog.wordpress.com/2018/06/27/node-js-v8-on-raspberry-pi-zero/
cd /home/pi
wget https://nodejs.org/dist/v8.11.3/node-v8.11.3-linux-armv6l.tar.xz
tar -xvf node-v8.11.3-linux-armv6l.tar.xz
cd node-v8.11.3-linux-armv6l
sudo cp -R * /usr/local/
cd ..
rm -Rf node-v8.11.3-linux-armv6l

# Bleno (for bt peripheral)
# Do this before bluez as it will be updated by better bluez bellow
cd /home/pi/VanTomation
sudo apt-get install -y bluetooth bluez libbluetooth-dev libudev-dev
npm install bleno
cd /home/pi

/home/pi/send-notification.sh "Setup node done"

# ngrok
cd /home/pi
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
unzip ngrok-stable-linux-arm.zip
rm ngrok-stable-linux-arm.zip

NGROK_AUTH_TOKEN=`cat /boot/ngrokauthtoken`
cp -f /home/pi/VanTomation/ngrok.ymp /home/pi/.ngrok2/ngrok.yml
echo "authtoken: $NGROK_AUTH_TOKEN" >> /home/pi/.ngrok2/ngrok.yml
sudo rm -f /boot/ngrokauthtoken

/home/pi/send-notification.sh "ngrok done"

# Installing bluez
sudo apt-get install -y libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.50.tar.xz
tar xvf bluez-5.50.tar.xz
rm bluez-5.50.tar.xz

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

# Make display work better for small screen
sudo sh -c 'echo "hdmi_ignore_hotplug=1" >> /boot/config.txt'
sudo sh -c 'echo "sdtv_mode=0" >> /boot/config.txt'
sudo sh -c 'echo "enable_uart=1" >> /boot/config.txt'
sudo sh -c 'echo "framebuffer_width=800" >> /boot/config.txt'
sudo sh -c 'echo "framebuffer_height=600" >> /boot/config.txt'

# No screen saver
# From https://www.raspberrypi.org/forums/viewtopic.php?t=57552
echo "@xset s noblank" >> /home/pi/.config/lxsession/LXDE-pi/autostart
echo "@xset s off" >> /home/pi/.config/lxsession/LXDE-pi/autostart
echo "@xset -dpms" >> /home/pi/.config/lxsession/LXDE-pi/autostart

# To start the monitor when the desktop starts
echo "@lxterminal -e bash -c -l /home/pi/VanTomation/monitor.py" >> /home/pi/.config/lxsession/LXDE-pi/autostart

# Open weather map API key
OWM_API_KEY=`cat /boot/owm_api_key`
echo "export OWM_API_KEY=$OWM_API_KEY" >> .bashrc
sudo rm -f /boot/owm_api_key

# https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md
# https://learn.adafruit.com/setting-up-a-raspberry-pi-as-a-wifi-access-point/install-software

sudo apt-get install -y hostapd dnsmasq
sudo cp VanTomation/config/iptables.ipv4.nat /etc/
sudo cp -f VanTomation/config/hostapd /etc/default/hostapd

PASS=`cat /boot/wifipass`
sed "s/PASSWORD/$PASS/" VanTomation/config/hostapd.conf > VanTomation/config/hostapd.conf.replaced
sudo mv -f VanTomation/config/hostapd.conf.replaced /etc/hostapd/hostapd.conf
sudo rm -f /boot/wifipass

sudo cp -f VanTomation/config/interfaces.ap /etc/network/interfaces
sudo cp -f VanTomation/config/dhcpcd.ap /etc/dhcpcd.conf
sudo cp -f VanTomation/config/dnsmasq.conf /etc/dnsmasq.conf

sudo update-rc.d hostapd enable

sudo sh -c 'cp -f /home/pi/VanTomation/rclocal.txt /etc/rc.local'
sudo sh -c 'chown root:root /etc/rc.local'
sudo sh -c 'chmod 755 /etc/rc.local'

sudo sh -c 'echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf'

# Dropbox uploader: https://github.com/andreafabrizi/Dropbox-Uploader
curl "https://raw.githubusercontent.com/andreafabrizi/Dropbox-Uploader/master/dropbox_uploader.sh" -o /home/pi/dropbox_uploader.sh
TOKEN=`cat /boot/dropboxtoken`
echo "OAUTH_ACCESS_TOKEN=$TOKEN" > /home/pi/.dropbox_uploader
sudo cp .dropbox_uploader /root/.dropbox_uploader
sudo chmod +x /home/pi/dropbox_uploader.sh
sudo rm -f /boot/dropboxtoken

# Download saved files
/home/pi/dropbox_uploader.sh download wpa_supplicant.conf wpa_supplicant.conf
sudo mv -f wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

# Save files when dhcp changes
sudo ln -s /home/pi/VanTomation/dhcp_up.sh /etc/dhcpcd.enter-hook

# For temperature controller
# From https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20
sudo sh -c 'echo "dtoverlay=w1-gpio" >> /boot/config.txt'

crontab VanTomation/config/crontab.txt
