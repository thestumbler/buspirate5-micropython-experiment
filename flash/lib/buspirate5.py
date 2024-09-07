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
import splash
import framebuf
import dplogo25

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
    self.io = bp5io.BP5IO(self.sr, self.disp)
    self.adc = analog.Analog(self.sr, self.disp)
    self.psu = power.Power(self.sr, self.adc)
    # not ready, do not use NAND
    # self.nand = nand.NAND(self.spi)
    self.splash()
    # make it easier to access each bit of the I/O connector
    self.b0 = self.io.bits[0]
    self.b1 = self.io.bits[1]
    self.b2 = self.io.bits[2]
    self.b3 = self.io.bits[3]
    self.b4 = self.io.bits[4]
    self.b5 = self.io.bits[5]
    self.b6 = self.io.bits[6]
    self.b7 = self.io.bits[7]

  # Convenience function to reset into bootloader
  def bootloader(self):
    """Reboot into the bootloader."""
    machine.bootloader()

  # Splash screen
  def splash(self, wait=False):
    """Display boot-up splash screen"""
    splash.screen(self.disp, nloops=1, nrotations=1, text="Bus Pirate 5")
    self.lamps.big_race(nloops=2)
    # wait for push button to proceed
    if wait:
      while not self.sw2():
        self.lamps.big_race(nloops=1)
    self.disp.cls()
    for row in range(self.disp.nrows):
      self.disp.text( f'Row {row}', row, row )

  # Logo random
  def splash_logo(self, wait=False):
    """Display logo randomly on screen"""
    icon = dplogo25.logo()
    icon.fb = framebuf.FrameBuffer(icon.buf, icon.wid, icon.hgt, 
              framebuf.RGB565) # monkey patch FB on icon object
    splash.logo(self.disp, icon, nloops=1 )
    self.lamps.big_race(nloops=2)
    # wait for push button to proceed
    if wait:
      while not self.sw2():
        self.lamps.big_race(nloops=1)
    self.disp.cls()
    for row in range(self.disp.nrows):
      self.disp.text( f'Row {row}', row, row )




