#!/bin/bash

# From https://docs.sainsmart.com/article/zn73h7h6b6-uploading-firmware-on-a-sain-smart-cnc-controller
# and https://github.com/xinabox/xLoader#flashing-on-non-windows-operating-systems

echo "This never worked so if actually needed you might need to tweak...."
exit 1

if [ -z $1 ] ; then
  echo "Usage: $0 <hex file>"
  exit 1
fi

if [ ! -f $1 ] ; then
  echo "File not found: $1"
  exit 2
fi

avrdude -v -v -p m328p -c stk500 -b 115200 -P /dev/ttyUSB0 -U flash:w:$1
