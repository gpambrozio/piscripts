#!/bin/bash

libcamera-vid -t 0 -n --width 800 --height 600 --inline -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/stream1}' :demux=h264
