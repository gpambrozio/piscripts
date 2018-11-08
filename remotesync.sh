#!/bin/bash

if [[ -z "$1" || -z "$2" ]] ; then
	echo "Usage: $0 machine-name machine-ip"
	exit 1
fi

listcommand="ls -lRT $1"

while true ; do
   newfilelist=$( $listcommand )
   if [[ $oldfilelist != $newfilelist ]] ; then
      oldfilelist=$newfilelist
      rsync --exclude='.*' --exclude='node_modules' --exclude='owm_icons' --delete --recursive --perms --itemize-changes --times --compress --human-readable --rsh=ssh "$1/" "pi@$2:/home/pi/$1/"
   fi
   sleep 1 || exit 2 
done
