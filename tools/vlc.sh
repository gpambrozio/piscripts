#!/bin/bash

DISPLAY=:0 cvlc --no-audio screen:// --screen-fps 2 --sout "#transcode{vcodec=MJPG,vb=800}:standard{access=http,mux=mpjpeg,dst=:8888/}" --sout-http-mime="multipart/x-mixed-replace;boundary=--7b3cc56e5f51db803f790dad720ed50a"