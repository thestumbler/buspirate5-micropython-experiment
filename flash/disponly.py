from machine import Pin, SPI
import machine
import time

from bp5pins import *
import lamps
import sr595
import display
import analog
import power
import bp5io
#import nand
from hexdump import hexdump
# use hello example for splash screen
# from splash import splash_screen
import framebuf
import bouncer

class BP5:
  '''Bus Pirate 5 RP2040 MicroPython proof-of-concept demo.
  Get help on each peripheral device class:
    lamps.help()   LED ring class
    disp.help()    TFT display
    adc.help()     analog to digital converter
    psu.help()     adjustable power supply
    io.help()      I/O connector pins class
    b0..b7         individual I/O pins classes
    sw2            push button (not class, just Pin)
  Functions:
    splash()       shows the splash screen
    bootloader()   enters the RP2040 bootloader
  See demo.py for some test scripts
  '''

  def help(self):
    print(self.__doc__)

  def __init__(self):
    self.spi = SPI(0, baudrate=16_0000_0000, 
               firstbit = SPI.MSB,
               polarity=0, phase=0, # defaults
               sck=Pin(PIN_SPI_CLK), 
               mosi=Pin(PIN_SPI_SDO), 
               miso=Pin(PIN_SPI_SDI)
            )
    # Create the modules
    self.sw2 = Pin(PIN_BUTTONS, Pin.IN, Pin.PULL_DOWN)
    self.lamps = lamps.Lamps()
    self.sr = sr595.SR(self.spi)
    self.disp = display.Display(self.spi, self.sr)

  def mkchaser(self):
    # instantiate Bouncer first, for some reason it clears the 
    # screen (making framebuffer maybe?)
    self.chaser = bouncer.Bouncer(self.disp, self.lamps, self.sw2)


b = BP5()
b.mkchaser()
