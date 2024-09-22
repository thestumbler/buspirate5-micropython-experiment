import neopixel
from machine import Pin
import time
from bp5pins import *

class Colors:
  red      = (255, 0, 0)
  green    = (0, 255, 0)
  blue     = (0, 0, 255)
  cyan     = (0, 255, 255)
  purple   = (255, 0, 255)
  yellow   = (255, 255, 0)
  white    = (255, 255, 255)
  black    = (0, 0, 0)


class Lamps:
  __doc__ = \
  '''Manages the chain of 18 each RGB LEDs arranged
  around the BP5 perimeter on the top and sides as follows:
    lamps = lamps.Lamps()
  Class functions:
    write()          sends accumulated commands to LED string
    fill(color)      send one color to all LEDs
    on(i, color)     turns on specified LED
    off(i)           turns off speficied LED
    only(i, color)   turns on speficied lamp, turning off previous 
    race()           LED race pattern (chase)
      group            which group (see below)
      color            color
      dwell            on time each LED, msec
      nloops           number laps around racetrack
  Constants:
    Predefined colors:   
      red, green, blue 
      cyan, purple, yellow
      white, black
    Groups of LEDs sorted by geometry:
      use map() function for help on mapping / groups'''

  def help(self):
    print(self.__doc__)

  def map(self):
    print( '''LED mapping by geometry:
  Groups:
    range(0:18)             all LEDs
    top                     all LEDs on the top
    side                    all LEDs on the sides
    north.[top|side|both]   the north LEDS
    south.[top|side|both]   the south LEDS
    east.[top|side|both]    the east LEDS
    west.[top|side|both]    the west LEDS
  Legend:
                        NORTH
    +--------------------------------------------+   
    | S             (10)      (8)                |
    | I  +----------------------------------+    |
    | D  |      (11)     (9)       (7)      |    |
    | E  |                                  |    |
    | S  | (12)  +-----------------+    (6) |    |
    |    |       |                 |   +----|    |
  W |(13)|       |                 |   |    |(5) | E
  E |    | T     |                 |   | C  |    | A
  S |    | O     |                 |   | O  |    | S
  T |    | P     |                 |   | N  |    | T
    |(14)|       |                 |   |    |(4) |
    |    |       |                 |   +----|    |
    |    | (15)  +-----------------+    (3) |    |
    |    |                                  |    |
    |    |      (16)     (0)       (2)      |    |
    |    +----------------------------------+    |
    |               (17)      (1)                |
    +--------------------------------------------+   
                        SOUTH''')

  top = (11, 9, 7, 6, 3, 2, 0, 16, 15, 12)
  side = (10, 8, 5, 4, 1, 17, 14, 13)
  class north:
    top = (11, 9, 7)
    side = (10, 8)
    both = (11, 9, 7, 10, 8 )
  class south:
    top = (16, 0, 2)
    side = (17, 1)
    both = (16, 17, 9, 1, 2)
  class west:
    top = (12, 15)
    side = (13, 14)
    both = (12,13,14,15)
  class east:
    top = (6, 3)
    side = (5, 4)
    both = (6,5,4,3)

  def __init__(self):
    self.num = 18
    self.sdo = Pin(PIN_RGB_CHAIN, Pin.OUT) 
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

  def on_group( self, group, color=Colors.red, dwell=25 ):
    for i in group:
      self.on(i, color)
    if dwell:
      time.sleep_ms(dwell)
      self.off_group( group )

  def off_group( self, group ):
    for i in group:
      self.off(i)

  def race(self, group, color=Colors.red, dwell=25, nloops=25):
    for n in range(nloops):
      for i in group:
        self.only(i, color)
        time.sleep_ms(dwell)
    self.off(self.last_lamp)

  def big_race(self, nloops=500):
    for n in range(nloops):
      self.race(self.top, color=Colors.red, dwell=25, nloops=1)
      self.race(self.side, color=Colors.blue, dwell=15, nloops=2)
    self.fill(Colors.black)




