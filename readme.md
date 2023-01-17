If you want USB serial console add:

`echo "enable_uart=1" >> /Volumes/boot/config.txt`

## Starting to install

ssh -o CheckHostIP=no -o StrictHostKeyChecking=no -o UpdateHostKeys=no -o UserKnownHostsFile=/dev/null pi@raspberrypi.local
wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/install.sh && chmod +x /home/pi/install.sh
/home/pi/install.sh <name>
