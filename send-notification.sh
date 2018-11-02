#!/bin/bash

wget --post-data "token=acMLorGZk7ZsWPQ3KcBwHHVr4tADtX&user=u8pxz9cSkbD9VJ5j6jTRiABjix5qF8&sound=bike&message=$1" -O - https://api.pushover.net/1/messages
