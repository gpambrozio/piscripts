#!/bin/bash

# We need to disable IPV6 otherwise this won't work
# From https://askubuntu.com/a/38468

sudo sh -c 'echo "precedence ::ffff:0:0/96  100" >> /etc/gai.conf'
wget --post-data "token=acMLorGZk7ZsWPQ3KcBwHHVr4tADtX&user=u8pxz9cSkbD9VJ5j6jTRiABjix5qF8&sound=bike&message=$1" -O - https://api.pushover.net/1/messages
