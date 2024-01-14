#!/bin/bash

set -euox pipefail
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

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/send-notification.sh
chmod +x send-notification.sh

IPS=`ifconfig | awk '/inet / {print $2}'`
/home/pi/send-notification.sh "Install started on $1: $IPS"

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/bash_aliases.sh
mv -f bash_aliases.sh ~/.bash_aliases
chmod +x ~/.bash_aliases

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/screenrc.txt
mv -f screenrc.txt ~/.screenrc

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get check || exit 0
sudo apt-get install -y git screen

# From https://stackoverflow.com/a/52269934
git clone -n --depth=1 --filter=tree:0 https://github.com/gpambrozio/piscripts
cd piscripts
git sparse-checkout set --no-cone "$1"
git checkout
cd ..
ln -s "piscripts/$1" "$1"

wget https://raw.githubusercontent.com/gpambrozio/piscripts/master/update.sh
chmod +x update.sh

/home/pi/send-notification.sh "Config started on $1"

./$1/install.sh
./$1/update.sh

# From https://forums.raspberrypi.com/search.php?author_id=288467&sr=posts&sid=fe3e671ff6a89f0f285bdb74d611e9fb
# Avoids setup wizard shown on startup
sudo rm /etc/xdg/autostart/piwiz.desktop

# Cleanup

sudo apt-get -y clean

/home/pi/send-notification.sh "Install done on $1."

if [ -f "/home/pi/$1/post-install.sh" ] ; then
  /home/pi/send-notification.sh "Remember to run '/home/pi/$1/post-install.sh' to finish your installation"
fi

rm -f "$0"
