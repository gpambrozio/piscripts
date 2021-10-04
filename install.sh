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
echo -n "$1" > install_name

# We need to disable IPV6 otherwise a lot of things doesn't work (like notifications)
# From https://askubuntu.com/a/38468
sudo sh -c 'echo "precedence ::ffff:0:0/96  100" >> /etc/gai.conf'

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/send-notification.sh
chmod +x send-notification.sh

IPS=`ifconfig | awk '/inet / {print $2}'`
/home/pi/send-notification.sh "Install started on $1: $IPS"

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/bash_aliases.sh
mv -f bash_aliases.sh ~/.bash_aliases
chmod +x ~/.bash_aliases

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/screenrc.txt
mv -f screenrc.txt ~/.screenrc

if [ -f /boot/authorized_keys ] ; then
    sudo mkdir /home/pi/.ssh
    sudo mv /boot/authorized_keys /home/pi/.ssh/
    sudo chown -R pi:pi /home/pi/.ssh
    sudo chmod 700 /home/pi/.ssh
    sudo chmod 600 /home/pi/.ssh/authorized_keys
fi

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get check || exit 0
sudo apt-get install -y subversion screen

svn checkout "https://github.com/gpambrozio/piscripts/trunk/$1"

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/update.sh
chmod +x update.sh

/home/pi/send-notification.sh "Config started on $1"

./$1/install.sh
./$1/update.sh

# Cleanup

sudo apt-get -y clean

/home/pi/send-notification.sh "Install done on $1."

if [ -f "/home/pi/$1/post-install.sh" ] ; then
  /home/pi/send-notification.sh "Remember to run '/home/pi/$1/post-install.sh' to finish your installation"
fi

rm -f "$0"
