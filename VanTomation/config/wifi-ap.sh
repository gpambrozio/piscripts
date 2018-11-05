cp /home/pi/Vantomation/config/interfaces.ap /etc/network/interfaces
cp /home/pi/dVantomation/config/hcpcd.ap /etc/dhcpcd.conf
service dhcpcd restart
ifdown wlan0
ifup wlan0
systemctl start hostapd
systemctl start dnsmasq
