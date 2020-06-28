Files with secrets to add before running install.sh:

* From ~/.ssh/id_rsa.pub: /boot/authorized_keys
* /boot/ssh to enable ssh access

## Starting to install

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/install.sh
chown pi:pi /home/pi/install.sh && chmod +x /home/pi/install.sh
/home/pi/install.sh <name>
