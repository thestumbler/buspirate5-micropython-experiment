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
import nand
from hexdump import hexdump
# use hello example for splash screen
from hello import hello

class BP5:
  """Bus Pirate 5 MicroPython Proof-of-Concept Demo"""

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
    self.io = bp5io.BP5IO(self.sr)
    self.disp = display.Display(self.spi, self.sr)
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
  def splash(self):
    """Display boot-up splash screen"""
    hello(self.disp, nloops=1, nrotations=1)
    self.lamps.big_race(nloops=2)
    self.disp.cls()
    for row in range(self.disp.nrows):
      self.disp.text( f'Row {row}', row, row )



  def pins(self):
    """Show I/O pin definitions on the screen"""
    self.disp.cls()
    for row, pinout in enumerate(self.io.pinout_strings):
      print(pinout)
      self.disp.text( pinout, row+1, 0 )
  



