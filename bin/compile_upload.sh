#!/bin/sh
MPY_CROSS='/files/tools/micropython/mpy-cross/build/mpy-cross'
$MPY_CROSS vga1_16x16.py
$MPY_CROSS vga1_16x32.py
$MPY_CROSS vga1_8x16.py
$MPY_CROSS vga1_8x8.py
$MPY_CROSS vga1_bold_16x16.py
$MPY_CROSS vga1_bold_16x32.py
$MPY_CROSS vga2_16x16.py
$MPY_CROSS vga2_16x32.py
$MPY_CROSS vga2_8x16.py
$MPY_CROSS vga2_8x8.py
$MPY_CROSS vga2_bold_16x16.py
$MPY_CROSS vga2_bold_16x32.py

# cd ..
# mpremote cp -r romfonts/*.mpy :
