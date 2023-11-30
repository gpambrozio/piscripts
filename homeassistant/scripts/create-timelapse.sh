#!/bin/bash

set -euo pipefail

IN_DIR="/config/www/cam_captures"
OUT_DIR="/config/www/timelapses"
PREFIX="$1"

N=$(ls ${IN_DIR}/${PREFIX}/${PREFIX}_*.jpg | wc -l)
if [ $N -gt 10 ] ; then
  ffmpeg -framerate 10 -pattern_type glob -i "${IN_DIR}/${PREFIX}/${PREFIX}_*.jpg" -c:v libx264 -pix_fmt yuv420p ${OUT_DIR}/${PREFIX}-`date +"%Y-%m-%d-%H-%M"`.mp4
fi

rm ${IN_DIR}/${PREFIX}/${PREFIX}_*.jpg
