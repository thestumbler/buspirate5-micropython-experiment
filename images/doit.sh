#!/bin/bash

# convert png to jpg and back
# need to get the png into RGBA format first
# there is probably an easier way to do this
# in imagemagick / convert
#
# * wrencher.png: PNG image data, 1318 x 1446, 8-bit/color RGBA, non-interlaced
# * wrencher.jpg: JPEG image data, JFIF standard 1.01, resolution (DPCM), 
#                 density 118x118, segment length 16, baseline, precision 8, 
#                 1318x1446, components 1
# * wrencher_rgba.png: PNG image data, 1318 x 1446, 8-bit grayscale, non-interlaced
# 
# * dplogo.png:   PNG image data, 218 x 256, 8-bit colormap, non-interlaced
# * dplogo.jpg:   JPEG image data, JFIF standard 1.01, aspect ratio, 
#                 density 1x1, segment length 16, baseline, precision 8, 
#                 218x256, components 3
# * dplogo_rgba.png: PNG image data, 218 x 256, 8-bit/color RGB, non-interlaced
#
# $ convert wrencher.png wrencher.jpg
# $ convert wrencher.jpg wrencher_rgba.png
# $ file wrencher.png
# $ file wrencher.jpg
# $ file wrencher_rgba.png

###   BASE="$1"
###   convert "$1"_orig.png "$1".jpg
###   convert "$1".jpg "$1".png
###   file "$1"_orig.png
###   file "$1".jpg
###   file "$1".png

# next convert to RGB565
# using heavily modified version of:
# https://github.com/CommanderRedYT/rgb565-converter.git (fetch)
#
# convert -resize 3% "$1".png "$1"-small.png
# rgb565-converter -b1 -i "$1"-small.png -o "$1".py

# color-type=2 means RGB
# color-type=6 means RGBA
# convert -resize 5% -define png:color-type=2 wrencher_orig.png ww.png
# convert -resize 5% -define png:color-type=6 wrencher_orig.png ww.png
# convert buslogo_orig.png -define png:color-type 2 -resize 20% bb.png
# convert buslogo_orig.png -define png:color-type=2 -resize 20% bb.png
