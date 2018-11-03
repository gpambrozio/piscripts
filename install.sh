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

# We need to disable IPV6 otherwise a lot of things doesn't work (like notifications)
# From https://askubuntu.com/a/38468
sudo sh -c 'echo "precedence ::ffff:0:0/96  100" >> /etc/gai.conf'

cd /home/pi
wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/send-notification.sh
chmod +x send-notification.sh
/home/pi/send-notification.sh "Install started on $1"

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/update.sh
chmod +x update.sh

sudo apt-get update
sudo apt-get install subversion screen -y

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/bash_aliases.sh
mv -f bash_aliases.sh ~/.bash_aliases
chmod +x ~/.bash_aliases

echo -n "$1" > install_name
svn checkout "https://github.com/gpambrozio/piscripts/trunk/$1"
./$1/install.sh

/home/pi/send-notification.sh "Install Done."
rm -f "$0"
