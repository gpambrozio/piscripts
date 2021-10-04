Files with secrets to add before running install.sh:

```
cp ~/.ssh/id_rsa.pub /Volumes/boot/authorized_keys
touch /Volumes/boot/ssh
echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
 ssid=\"\"
 psk=\"\"
}" > /Volumes/boot/wpa_supplicant.conf 
mate /Volumes/boot/wpa_supplicant.conf
```

If you want USB serial console add:

`echo "enable_uart=1" >> /Volumes/boot/config.txt`

## Starting to install

ssh -o CheckHostIP=no -o StrictHostKeyChecking=no -o UpdateHostKeys=no -o UserKnownHostsFile=/dev/null pi@raspberrypi.local
wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/install.sh && chmod +x /home/pi/install.sh
/home/pi/install.sh <name>
