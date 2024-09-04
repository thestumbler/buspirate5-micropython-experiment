import neopixel
from machine import Pin
import time

class Colors:
  red      = (255, 0, 0)
  green    = (0, 255, 0)
  blue     = (0, 0, 255)
  cyan     = (0, 255, 255)
  purple   = (255, 0, 255)
  yellow   = (255, 255, 0)
  white    = (255, 255, 255)
  black    = (0, 0, 0)

# strip of 18 LEDs connected on GPIO.17
'''
                           NORTH
       +--------------------------------------------+   
       | SIDES         [10]      [8]                |
       |    +----------------------------------+    |
       |    |      [11]     [9]       [7]      |    |
       |    |                                  |    |
       |    |  [12] +-----------------+ [6]    |    |
       |    |       |                 |   +----|    |
       |[13]|       |                 |   |    |[5] |
       |    |       |                 |   |    |    |
  WEST |    | TOP   |                 |   |    |    | EAST
       |    |       |                 |   |    |    |
       |[14]|       |                 |   |    |[4] |
       |    |       |                 |   +----|    |
       |    |  [15] +-----------------+ [3]    |    |
       |    |                                  |    |
       |    |      [16]     [0]       [2]      |    |
       |    +----------------------------------+    |
       |               [17]      [1]                |
       +--------------------------------------------+   
                           SOUTH               
'''

class Lamps:
  top = (11, 9, 7, 6, 3, 2, 0, 16, 15, 12)
  side = (10, 8, 5, 4, 1, 17, 14, 13)
  class north:
    top = (11, 9, 7)
    side = (10, 8)
    north = (11, 9, 7, 10, 8 )
  class south:
    top = (16, 0, 2)
    side = (17, 1)
    south = (16, 17, 9, 1, 2)
  class west:
    top = (12, 15)
    side = (13, 14)
    west = (12,13,14,15)
  class east:
    top = (6, 3)
    side = (5, 4)
    east = (6,5,4,3)

  
  def __init__(self):
    self.num = 18
    self.sdo = Pin(17, Pin.OUT) 
    self.np = neopixel.NeoPixel(self.sdo, self.num)
    self.last_lamp = None

  def write(self):
    self.np.write()

  # force all LEDs same color
  def fill(self, _color):
    self.np.fill(_color)
    self.write()

  def on(self, ilamp, color=Colors.red):
    self.np[ilamp] = color
    self.write()

  def off(self, ilamp):
    self.np[ilamp] = Colors.black
    self.write()

  def only(self, ilamp, color=Colors.red):
    if self.last_lamp is None: self.last_lamp = ilamp
    self.np[self.last_lamp] = Colors.black
    self.np[ilamp] = color
    self.write()
    self.last_lamp = ilamp

  def race(self, group, color=Colors.red, dwell=25, nloops=25):
    for n in range(nloops):
      for i in group:
        self.only(i, color)
        time.sleep_ms(dwell)

  def big_race(self, nloops=500):
    for n in range(nloops):
      self.race(self.top, color=Colors.red, dwell=25, nloops=1)
      self.race(self.side, color=Colors.blue, dwell=15, nloops=2)
    self.fill(Colors.black)




