Files with secrets to add before running install.sh:

* cp ~/.ssh/id_rsa.pub /Volumes/boot/authorized_keys
* touch /Volumes/boot/ssh
* /boot/wpa_supplicant.conf to connect to wifi:

ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
 ssid=""
 psk=""
}

If you want USB serial console add:

enable_uart=1

to /boot/config.txt

## Starting to install

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/install.sh
chown pi:pi /home/pi/install.sh && chmod +x /home/pi/install.sh
/home/pi/install.sh <name>
