#!/bin/bash

if [[ -z "$1" ]] ; then
	echo "Usage: $0 machine-name [machine-ip]"
	exit 1
fi

MACHINE="$1"
if [[ -z "$2" ]] ; then
   MACHINE_IP="$1.local"
else
   MACHINE_IP="$2"
fi

listcommand="ls -lRT ${MACHINE}"

while true ; do
   newfilelist=$( $listcommand )
   if [[ $oldfilelist != $newfilelist ]] ; then
      oldfilelist=$newfilelist
      rsync --exclude='.*' --exclude='node_modules' --exclude='owm_icons' --exclude='*.pyc' --delete --recursive --perms --itemize-changes --times --compress --human-readable --rsh=ssh "${MACHINE}/" "pi@${MACHINE_IP}:/home/pi/${MACHINE}/"
      ssh pi@${MACHINE_IP} "/home/pi/${MACHINE}/update.sh"
   fi
   sleep 1 || exit 2 
done
