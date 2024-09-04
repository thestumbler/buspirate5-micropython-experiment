from machine import Pin, SPI
import st7789py as st7789
import vga2_bold_16x32 as font16
from bp5pins import *

class Display:
  TFA = 40
  BFA = 40
  WIDE = 1
  TALL = 0
  SCROLL = 0      # orientation for scroll.py
  FEATHERS = 1    # orientation for feathers.py

  def __init__(self, spi, sr, rotation = 0):
    self.sr = sr # shift register
    self.spi = spi
    self.cs = Pin(PIN_DISPLAY_CS, Pin.OUT)
    self.dp = Pin(PIN_DISPLAY_DP, Pin.OUT)
    self.rotation = rotation
    self.backlight(True)
    self.width = 240
    self.height = 320
    self.ncols = int(self.width / font16.WIDTH)
    self.nrows = int(self.height / font16.HEIGHT)
    # print(f'ROWS x COLS: {self.nrows} x {self.ncols}' )
    self.tft = st7789.ST7789(
        self.spi, 
        self.width,
        self.height,
        reset=None,
        cs=self.cs,
        dc=self.dp,
        backlight=None,
        rotation=self.rotation)
    self.cls()

  def backlight(self, light):
    self.light = light
    if self.light:
      self.sr.set_bits( self.sr.MASK_DISPLAY_BACKLIGHT )
    else:
      self.sr.clr_bits( self.sr.MASK_DISPLAY_BACKLIGHT )
    self.sr.send()

  def cls(self):
    self.tft.rotation(0)
    self.tft.fill(0)

  def text(self, text, row, col, 
           font = font16, 
           color = st7789.WHITE, 
           background = st7789.BLACK ):
    col = col % self.ncols
    row = row % self.nrows
    x0 = col * font.WIDTH
    y0 = row * font.HEIGHT
    self.tft.text( font, text, x0, y0, color, background )

