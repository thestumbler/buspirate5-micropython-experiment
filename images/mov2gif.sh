#!/bin/bash

# ffmpeg -i logo-bouncer.mov \
#   -filter:v "crop=1080:1080:0:400" \
#   logo-bouncer-cropped.mov

ffmpeg -i logo-bouncer-cropped.mov \
-r 15 \
  -vf scale=140:-1 \
  -ss 00:00:03 -to 00:00:06 \
  out.gif
