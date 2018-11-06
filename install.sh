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

IPS=`ifconfig 2 > /dev/null | awk '/inet / {print $2}'`
/home/pi/send-notification.sh "Install started on $1: $IPS"

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/bash_aliases.sh
mv -f bash_aliases.sh ~/.bash_aliases
chmod +x ~/.bash_aliases

sudo apt-get update
sudo apt-get install -y subversion screen

svn checkout "https://github.com/gpambrozio/piscripts/trunk/$1"

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/update.sh
chmod +x update.sh

/home/pi/send-notification.sh "Config started on $1"

./$1/install.sh

/home/pi/send-notification.sh "Install done on $1."
rm -f "$0"
