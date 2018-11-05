cp /home/pi/Vantomation/config/interfaces.client /etc/network/interfaces
cp /home/pi/Vantomation/config/dhcpcd.client /etc/dhcpcd.conf
systemctl stop dnsmasq
systemctl stop hostapd
service dhcpcd restart
ifdown wlan0
ifup wlan0
